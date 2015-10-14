# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    @api.depends('product_id', 'qty', 'product_id.weight',
                 'product_id.weight_net', 'product_id.volume')
    def _compute_totals(self):
        for record in self:
            record.total_weight = record.product_id.weight * record.qty
            record.total_weight_net = record.product_id.weight_net * record.qty
            record.total_volume = record.product_id.volume * record.qty

    weight = fields.Float(string='Weight', related='product_id.weight')
    weight_net = fields.Float(
        string='Net Weight', related='product_id.weight_net')
    volume = fields.Float(
        string='Volume', related='product_id.volume')
    total_weight = fields.Float(
        string='Total weight', compute='_compute_totals')
    total_weight_net = fields.Float(
        string='Total Net weight', compute='_compute_totals')
    total_volume = fields.Float(
        string='Total Volume', compute='_compute_totals')


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    @api.multi
    @api.depends('height', 'width', 'length', 'quant_ids',
                 'quant_ids.total_weight', 'quant_ids.total_weight_net',
                 'quant_ids.total_volume', 'children_ids',
                 'children_ids.total_weight', 'children_ids.empty_weight',
                 'children_ids.total_weight_net', 'children_ids.total_volume')
    def _compute_totals(self):
        for record in self:
            record.total_weight = sum(x.total_weight for x in record.quant_ids)
            record.total_weight_net = sum(x.total_weight_net for x in
                                          record.quant_ids)
            record.total_volume = sum(x.total_volume for x in record.quant_ids)
            record.total_estim_weight = (
                record.total_weight + record.empty_weight +
                sum(x.total_weight + x.empty_weight for x in
                    record.children_ids))
            record.real_weight = record.total_estim_weight
            record.total_estim_weight_net = (
                record.total_weight_net + record.empty_weight +
                sum(x.total_weight_net + x.empty_weight for x in
                    record.children_ids))
            record.tvolume_charge = (
                record.total_volume + sum(x.total_volume for x in
                                          record.children_ids))
            record.permitted_volume = (
                record.height * record.width * record.length)

    @api.multi
    def _compute_pickings(self):
        for record in self:
            record.pickings = self.env['stock.pack.operation'].search(
                [('result_package_id', '=', record.id)]).mapped('picking_id')

    height = fields.Float(string='Height', help='The height of the package')
    width = fields.Float(string='Width', help='The width of the package')
    length = fields.Float(string='Length', help='The length of the package')
    empty_weight = fields.Float(string='Empty Package Weight')
    real_weight = fields.Float(string='Real Weight')
    total_weight = fields.Float(
        string='Total Weight', compute='_compute_totals')
    total_weight_net = fields.Float(
        string='Total Net Weight', compute='_compute_totals')
    total_volume = fields.Float(
        string='Total Volume', compute='_compute_totals')
    total_estim_weight = fields.Float(
        string='Total Estimated Weight', compute='_compute_totals')
    total_estim_weight_net = fields.Float(
        string='Total Estimated Net Weight', compute='_compute_totals')
    permitted_volume = fields.Float(
        string='Permitted volume', compute='_compute_totals')
    tvolume_charge = fields.Float(
        string='Total volume charge', compute='_compute_totals')
    pickings = fields.Many2many(
        comodel_name='stock.picking', string='Pickings',
        compute='_compute_pickings')

    @api.multi
    @api.onchange('ul_id')
    def onchange_ul_id(self):
        for record in self:
            record.height = record.ul_id.height
            record.width = record.ul_id.width
            record.length = record.ul_id.length
            record.empty_weight = record.ul_id.weight

    @api.model
    def create(self, values):
        if values.get('ul_id', False):
            ul = self.env['product.ul'].browse(values.get('ul_id'))
            values.update({
                'height': ul.height,
                'width': ul.width,
                'length': ul.length,
                'empty_weight': ul.weight,
            })
        return super(StockQuantPackage, self).create(values)
