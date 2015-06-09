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

    @api.one
    @api.depends('pack_operation_ids', 'pack_operation_ids.result_package_id')
    def _calc_picking_packages(self):
        self.packages = self.pack_operation_ids.mapped('result_package_id')

    @api.one
    @api.depends('packages', 'packages.ul_id')
    def _calc_picking_packages_info(self):
        pack_weight = self.env['stock.picking.package.weight.lot']
        pack_weight_obj = self.env['stock.picking.package.weight.lot']
        pack_total = self.env['stock.picking.package.total']
        pack_total_obj = self.env['stock.picking.package.total']
        sequence = 0
        for package in self.packages:
            sequence += 1
            package_operations = self.pack_operation_ids.filtered(
                lambda r: r.result_package_id == package)
            total_weight = 0.0
            for pack_operation in package_operations:
                total_weight += (pack_operation.product_qty *
                                 pack_operation.product_id.weight)
            vals = {
                'picking': self.id,
                'sequence': sequence,
                'package': package.id,
                'lots': [(6, 0, (package.quant_ids.mapped('lot_id').ids or
                                 package_operations.mapped('lot_id').ids))],
                'net_weight': total_weight,
                'gross_weight': total_weight + package.empty_weight,
            }
            pack_weight += pack_weight_obj.create(vals)
        if self.packages:
            for product_ul in self.env['product.ul'].search([]):
                cont = len(self.packages.filtered(
                    lambda x: x.ul_id.id == product_ul.id))
                if cont:
                    vals = {
                        'picking': self.id,
                        'ul': product_ul.id,
                        'quantity': cont,
                    }
                    pack_total += pack_total_obj.create(vals)
        self.packages_info = pack_weight
        self.package_totals = pack_total
        self.num_packages = sum(x.quantity for x in self.package_totals)

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
