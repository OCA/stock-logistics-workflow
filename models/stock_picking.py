# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp


class StockPickingPackageWeightLot(models.Model):
    _name = 'stock.picking.package.weight.lot'
    _description = 'Stock Picking Package Weight Total'
    _order = 'sequence'

    picking = fields.Many2one(
        comodel_name='stock.picking', string='Picking')
    sequence = fields.Integer(string='Sequence')
    package = fields.Many2one(
        comodel_name='stock.quant.package', string='Package')
    lots = fields.Many2many(
        comodel_name='stock.production.lot', string='Lots/Serial Numbers',
        relation='rel_package_weight_lot')
    net_weight = fields.Float(
        string='Net Weight', digits=dp.get_precision('Stock Weight'))
    gross_weight = fields.Float(
        string='Gross Weight', digits=dp.get_precision('Stock Weight'))


class StockPickingPackageTotal(models.Model):
    _name = 'stock.picking.package.total'
    _description = 'Stock Picking Package Total'

    picking = fields.Many2one(
        comodel_name='stock.picking', string='Picking')
    ul = fields.Many2one(
        comodel_name='product.ul', string='Logistic Unit')
    quantity = fields.Integer(string='# Packages')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    @api.depends('pack_operation_ids', 'pack_operation_ids.result_package_id')
    def _calc_picking_packages(self):
        for record in self:
            record.packages = record.pack_operation_ids.mapped(
                'result_package_id')

    @api.multi
    @api.depends('packages', 'packages.ul_id')
    def _calc_picking_packages_info(self):
        pack_weight = self.env['stock.picking.package.weight.lot']
        pack_weight_obj = self.env['stock.picking.package.weight.lot']
        pack_total = self.env['stock.picking.package.total']
        pack_total_obj = self.env['stock.picking.package.total']
        for record in self:
            sequence = 0
            for package in record.packages:
                sequence += 1
                package_operations = record.pack_operation_ids.filtered(
                    lambda r: r.result_package_id == package)
                total_weight = 0.0
                for pack_operation in package_operations:
                    total_weight += (pack_operation.product_qty *
                                     pack_operation.product_id.weight)
                vals = {
                    'picking': record.id,
                    'sequence': sequence,
                    'package': package.id,
                    'lots': [(6, 0,
                              (package.quant_ids.mapped('lot_id').ids or
                               package_operations.mapped('lot_id').ids))],
                    'net_weight': total_weight,
                    'gross_weight': total_weight + package.empty_weight,
                }
                pack_weight += pack_weight_obj.create(vals)
            if record.packages:
                for product_ul in self.env['product.ul'].search([]):
                    cont = len(record.packages.filtered(
                        lambda x: x.ul_id.id == product_ul.id))
                    if cont:
                        vals = {
                            'picking': record.id,
                            'ul': product_ul.id,
                            'quantity': cont,
                        }
                        pack_total += pack_total_obj.create(vals)
            record.packages_info = pack_weight
            record.package_totals = pack_total
            record.num_packages = sum(x.quantity for x in
                                      record.package_totals)

    packages = fields.Many2many(
        comodel_name='stock.quant.package', string='Packages',
        compute='_calc_picking_packages')
    packages_info = fields.One2many(
        comodel_name='stock.picking.package.weight.lot',
        inverse_name='picking', string='Packages Info',
        compute='_calc_picking_packages_info')
    package_totals = fields.One2many(
        comodel_name='stock.picking.package.total', inverse_name='picking',
        string='Total UL Packages Info', compute='_calc_picking_packages_info')
    num_packages = fields.Integer(
        string='# Packages', compute='_calc_picking_packages_info')

    @api.multi
    def create_all_move_packages(self):
        location_obj = self.env['stock.location']
        pack_op_obj = self.env['stock.pack.operation']
        for picking in self:
            for move in picking.move_lines:
                op_qty = sum([x.product_qty for x in
                              move.mapped('linked_move_operation_ids.'
                                          'operation_id')])
                if not move.product_qty - op_qty > 0:
                    continue
                location_dest = location_obj.get_putaway_strategy(
                    picking.location_dest_id, move.product_id) or \
                    picking.location_dest_id
                val_dict = {
                    'picking_id': picking.id,
                    'product_qty': move.product_qty - op_qty,
                    'product_id': move.product_id.id,
                    'package_id': False,
                    'lot_id': False,
                    'owner_id': picking.owner_id.id,
                    'location_id': picking.location_id.id,
                    'location_dest_id': location_dest.id,
                    'product_uom_id': move.product_id.uom_id.id,
                    }
                pack_op_obj.create(val_dict)
        return True
