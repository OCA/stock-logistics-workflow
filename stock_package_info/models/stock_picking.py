# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2015-2018 Tecnativa - Pedro M. Baeza
# Copyright 2015 AvanzOsc
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    package_ids = fields.Many2many(
        comodel_name='stock.quant.package',
        string='Packages',
        compute='_compute_picking_packages',
    )
    package_info_ids = fields.Many2many(
        comodel_name='stock.picking.package.weight.lot',
        relation='stock_picking_package_info_ids',
        string='Packages Info',
        compute='_compute_picking_package_info_ids',
    )
    package_total_ids = fields.Many2many(
        comodel_name='stock.picking.package.total',
        relation='stock_picking_packages_total',
        string='Total UL Packages Info',
        compute='_compute_picking_package_info_ids'
    )
    num_packages = fields.Integer(
        string='Number of Packages',
        compute='_compute_picking_package_info_ids',
    )

    @api.multi
    def _compute_picking_packages(self):
        for record in self:
            package_ids = set(
                record.pack_operation_ids.mapped('result_package_id.id') +
                record.pack_operation_ids.mapped('package_id.id'),
            )
            record.package_ids = [(6, 0, package_ids)]

    @api.multi
    def _compute_picking_package_info_ids(self):

        pack_weight_obj = self.env['stock.picking.package.weight.lot']
        pack_total_obj = self.env['stock.picking.package.total']

        for record in self:

            pack_weight = self.env['stock.picking.package.weight.lot']
            pack_total = self.env['stock.picking.package.total']
            product_packages = defaultdict(int)
            sequence = 0

            for package in record.package_ids:

                sequence += 1
                total_weight = sum([
                    (x.qty * x.product_id.weight) for x in package.quant_ids
                ])
                lots = package.quant_ids.mapped('lot_id')

                pack_weight += pack_weight_obj.create({
                    'sequence': sequence,
                    'package_id': package.id,
                    'lot_ids': [(6, 0, lots.ids)],
                    'net_weight': total_weight,
                    'gross_weight': total_weight + package.empty_weight,
                })

                if package.packaging_id:
                    product_packages[package.packaging_id] += 1

            for product_package, qty in product_packages.items():
                pack_total += pack_total_obj.create({
                    'product_packaging_id': product_package.id,
                    'quantity': qty,
                })

            record.package_info_ids = [(6, 0, pack_weight.ids)]
            record.package_total_ids = [(6, 0, pack_total.ids)]
            record.num_packages = sum(x.quantity for x in pack_total)

    @api.multi
    def create_all_move_packages(self):
        pack_op_obj = self.env['stock.pack.operation']
        ops = self.env['stock.pack.operation']
        for picking in self:
            forced_qties = defaultdict(int)
            picking_quants = self.env['stock.quant']
            for move in picking.move_lines:
                if move.state not in ('assigned', 'confirmed', 'waiting'):
                    continue
                move_quants = move.reserved_quant_ids
                picking_quants += move_quants
                forced_qty = (move.state == 'assigned') and \
                    move.product_qty - sum([x.qty for x in move_quants]) or 0
                rounding = move.product_id.uom_id.rounding
                if float_compare(forced_qty, 0,
                                 precision_rounding=rounding) > 0:
                    forced_qties[move.product_id] += forced_qty
            pack_ops = picking._prepare_pack_ops(picking_quants, forced_qties)
            for pack_op_vals in pack_ops:
                domain = [('picking_id', '=', picking.id)]
                if pack_op_vals.get('lot_id'):
                    domain += [('lot_id', '=', pack_op_vals['lot_id'])]
                if pack_op_vals.get('product_id'):
                    domain += [('product_id', '=', pack_op_vals['product_id'])]
                packs = pack_op_obj.search(domain)
                if packs:
                    qty = sum([x.product_qty for x in packs])
                    new_qty = pack_op_vals.get('product_qty', 0) - qty
                    if new_qty > 0:
                        pack_op_vals['product_qty'] = new_qty
                    else:
                        continue
                ops |= pack_op_obj.create(pack_op_vals)
        return ops

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        for picking in self.filtered('pack_operation_ids'):
            picking.create_all_move_packages()
        return res
