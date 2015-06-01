# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.one
    @api.depends('product_id', 'qty', 'product_id.weight',
                 'product_id.weight_net', 'product_id.volume')
    def _calculate_totals(self):
        self.total_weight = self.product_id.weight * self.qty
        self.total_weight_net = self.product_id.weight_net * self.qty
        self.total_volume = self.product_id.volume * self.qty

    weight = fields.Float(string='Weight', related='product_id.weight')
    weight_net = fields.Float(
        string='Net Weight', related='product_id.weight_net')
    volume = fields.Float(
        string='Volume', related='product_id.volume')
    total_weight = fields.Float(
        string='Total weight', compute='_calculate_totals')
    total_weight_net = fields.Float(
        string='Total Net weight', compute='_calculate_totals')
    total_volume = fields.Float(
        string='Total Volume', compute='_calculate_totals')


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    @api.one
    @api.depends('height', 'width', 'length', 'quant_ids',
                 'quant_ids.total_weight', 'quant_ids.total_weight_net',
                 'quant_ids.total_volume', 'children_ids',
                 'children_ids.total_weight', 'children_ids.empty_weight',
                 'children_ids.total_weight_net', 'children_ids.total_volume')
    def _calculate_totals(self):
        self.total_weight = sum(x.total_weight for x in self.quant_ids)
        self.total_weight_net = sum(x.total_weight_net for x in self.quant_ids)
        self.total_volume = sum(x.total_volume for x in self.quant_ids)
        self.total_estim_weight = (
            self.total_weight + self.empty_weight +
            sum(x.total_weight + x.empty_weight for x in self.children_ids))
        self.real_weight = self.total_estim_weight
        self.total_estim_weight_net = (
            self.total_weight_net + self.empty_weight +
            sum(x.total_weight_net + x.empty_weight for x in
                self.children_ids))
        self.tvolume_charge = (
            self.total_volume + sum(x.total_volume for x in self.children_ids))
        self.permitted_volume = self.height * self.width * self.length

    height = fields.Float(string='Height', help='The height of the package')
    width = fields.Float(string='Width', help='The width of the package')
    length = fields.Float(string='Length', help='The length of the package')
    empty_weight = fields.Float(string='Empty Package Weight')
    real_weight = fields.Float(string='Real Weight')
    total_weight = fields.Float(
        string='Total Weight', compute='_calculate_totals')
    total_weight_net = fields.Float(
        string='Total Net Weight', compute='_calculate_totals')
    total_volume = fields.Float(
        string='Total Volume', compute='_calculate_totals')
    total_estim_weight = fields.Float(
        string='Total Estimated Weight', compute='_calculate_totals')
    total_estim_weight_net = fields.Float(
        string='Total Estimated Net Weight', compute='_calculate_totals')
    permitted_volume = fields.Float(
        string='Permitted volume', compute='_calculate_totals')
    tvolume_charge = fields.Float(
        string='Total volume charge', compute='_calculate_totals')

#     pickings = fields.Many2many(
#         comodel_name='stock.picking',
#         relation='rel_picking_package', column1='package_id',
#         column2='picking_id', string='Pickings')

    @api.one
    @api.onchange('ul_id')
    def onchange_ul_id(self):
        self.height = self.ul_id.height
        self.width = self.ul_id.width
        self.length = self.ul_id.length
        self.empty_weight = self.ul_id.weight

    @api.one
    def create(self, values):
        if values.get('ul_id', False):
            ul = self.env['product.ul'].browse(values.get('ul_id'))
            values.update({
                'height': ul.height,
                'width': ul.width,
                'length': ul.length,
                'empty_weight': ul.empty_weight,
            })
        super(StockQuantPackage, self).create(values)
