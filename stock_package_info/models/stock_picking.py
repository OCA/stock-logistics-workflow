# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2015 AvanzOsc
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
        for rec_id in self:
            rec_id.package_ids = (rec_id.pack_operation_ids.mapped(
                'result_package_id') | rec_id.pack_operation_ids.mapped(
                'package_id'))

    @api.multi
    def _compute_picking_package_info_ids(self):
        pack_weight_obj = self.env['stock.picking.package.weight.lot']
        pack_total_obj = self.env['stock.picking.package.total']
        for record in self:
            record.package_info_ids.unlink()
            record.package_total_ids.unlink()
            pack_weight = self.env['stock.picking.package.weight.lot']
            pack_total = self.env['stock.picking.package.total']
            packages = (record.pack_operation_ids.mapped('result_package_id') |
                        record.pack_operation_ids.mapped('package_id'))
            sequence = 0
            for package in packages:
                sequence += 1
                total_weight = sum([(x.qty * x.product_id.weight) for x
                                    in package.quant_ids])
                lots = (package.quant_ids.mapped('lot_id').ids or [])
                vals = {
                    'sequence': sequence,
                    'package_id': package.id,
                    'lot_ids': [(6, 0, lots)],
                    'net_weight': total_weight,
                    'gross_weight': total_weight + package.empty_weight,
                }
                pack_weight += pack_weight_obj.create(vals)
            if packages:
                for tmpl in packages.mapped('product_pack_tmpl_id'):
                    cont = len(packages.filtered(
                        lambda x: x.product_pack_tmpl_id.id == tmpl.id))
                    vals = {
                        'product_pack_tmpl_id': tmpl.id,
                        'quantity': cont,
                    }
                    pack_total += pack_total_obj.create(vals)
            record.package_info_ids = pack_weight
            record.package_total_ids = pack_total
            record.num_packages = sum(x.quantity for x in pack_total)

    @api.multi
    def create_all_move_packages(self):
        pack_op_obj = self.env['stock.pack.operation']
        ops = self.env['stock.pack.operation']
        for picking in self:
            forced_qties = {}
            picking_quants = []
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
                    if forced_qties.get(move.product_id):
                        forced_qties[move.product_id] += forced_qty
                    else:
                        forced_qties[move.product_id] = forced_qty
            for vals in picking._prepare_pack_ops(
                    picking, picking_quants, forced_qties):
                domain = [('picking_id', '=', picking.id)]
                if vals.get('lot_id', False):
                    domain += [('lot_id', '=', vals['lot_id'])]
                if vals.get('product_id', False):
                    domain += [('product_id', '=', vals['product_id'])]
                packs = pack_op_obj.search(domain)
                if packs:
                    qty = sum([x.product_qty for x in packs])
                    new_qty = vals.get('product_qty', 0) - qty
                    if new_qty > 0:
                        vals['product_qty'] = new_qty
                    else:
                        continue
                ops |= pack_op_obj.create(vals)
        return ops
