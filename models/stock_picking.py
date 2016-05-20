# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp
from openerp.tools.float_utils import float_compare


class StockPickingPackageWeightLot(models.Model):
    _name = 'stock.picking.package.weight.lot'
    _description = 'Stock Picking Package Weight Total'
    _order = 'sequence'

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

    ul = fields.Many2one(
        comodel_name='product.ul', string='Logistic Unit')
    quantity = fields.Integer(string='# Packages')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    @api.depends('pack_operation_ids', 'pack_operation_ids.result_package_id')
    def _calc_picking_packages(self):
        for record in self:
            record.packages = (record.pack_operation_ids.mapped(
                'result_package_id') | record.pack_operation_ids.mapped(
                'package_id'))

    @api.multi
    @api.depends('pack_operation_ids', 'pack_operation_ids.result_package_id',
                 'pack_operation_ids.result_package_id.ul_id')
    def _calc_picking_packages_info(self):
        pack_weight_obj = self.env['stock.picking.package.weight.lot']
        pack_total_obj = self.env['stock.picking.package.total']
        for record in self:
            record.packages_info.unlink()
            record.package_totals.unlink()
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
                    'package': package.id,
                    'lots': [(6, 0, lots)],
                    'net_weight': total_weight,
                    'gross_weight': total_weight + package.empty_weight,
                }
                pack_weight += pack_weight_obj.create(vals)
            if packages:
                for product_ul in packages.mapped('ul_id'):
                    cont = len(packages.filtered(
                        lambda x: x.ul_id.id == product_ul.id))
                    vals = {
                        'ul': product_ul.id,
                        'quantity': cont,
                    }
                    pack_total += pack_total_obj.create(vals)
            record.packages_info = pack_weight
            record.package_totals = pack_total
            record.num_packages = sum(x.quantity for x in pack_total)

    packages = fields.Many2many(
        comodel_name='stock.quant.package', string='Packages',
        compute='_calc_picking_packages')
    packages_info = fields.Many2many(
        comodel_name='stock.picking.package.weight.lot',
        relation='stock_picking_packages_info', string='Packages Info',
        compute='_calc_picking_packages_info')
    package_totals = fields.Many2many(
        comodel_name='stock.picking.package.total',
        relation='stock_picking_packages_total',
        string='Total UL Packages Info', compute='_calc_picking_packages_info')
    num_packages = fields.Integer(
        string='# Packages', compute='_calc_picking_packages_info')

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
                    domain += [('lot_id', '=', vals.get('lot_id'))]
                if vals.get('product_id', False):
                    domain += [('product_id', '=',
                                vals.get('product_id'))]
                packs = pack_op_obj.search(domain)
                if packs:
                    qty = sum([x.product_qty for x in packs])
                    new_qty = vals.get('product_qty', 0) - qty
                    if new_qty > 0:
                        vals.update({'product_qty': new_qty})
                    else:
                        continue
                ops |= pack_op_obj.create(vals)
        return ops
