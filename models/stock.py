# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    packages = fields.Many2many(
        comodel_name='stock.quant.package',
        relation='rel_picking_package', column1='picking_id',
        column2='package_id', string='Packages')
    total_ul_packages_info = fields.One2many(
        "stock.picking.total.ul.package.info", "picking",
        string="Total UL Packages Info", readonly=True)
    num_packages = fields.Integer(string='Num. Packages', readonly=True)

    def _catch_operations(self):
        self.packages = [
            operation.result_package_id.id for operation in
            self.pack_operation_ids if operation.result_package_id]
        self. _calculate_total_ul_packages_info()

    def _calculate_total_ul_packages_info(self):
        package_datas = {}
        if self.total_ul_packages_info:
            self.total_ul_packages_info.unlink()
        for package in self.packages:
            found = False
            for data in package_datas:
                datos_array = package_datas[data]
                ul_id = datos_array['ul_id']
                quantity = datos_array['quantity']
                if ul_id == package.ul_id.id:
                    found = True
                    quantity += 1
                    package_datas[data].update({'quantity': quantity})
                    break
            if not found:
                package_datas[(package.ul_id.id)] = {'ul_id': package.ul_id.id,
                                                     'quantity': 1}
        self.num_packages = 0
        for data in package_datas:
            datos_array = package_datas[data]
            values = {'picking': self.id,
                      'ul': datos_array['ul_id'],
                      'quantity': datos_array['quantity']}
            self.env['stock.picking.total.ul.package.info'].create(values)
            self.num_packages += datos_array['quantity']


class StockPickingTotalUlPackageInfo(models.Model):
    _name = 'stock.picking.total.ul.package.info'
    _description = "Stock Picking Total UL Package Info"

    picking = fields.Many2one('stock.picking', string='Picking')
    ul = fields.Many2one('product.ul', string='Logistic Unit')
    quantity = fields.Integer(string='Num. Packages')


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.one
    @api.depends('product_id', 'product_id.weight', 'qty')
    def _calculate_total_weight(self):
        self.total_weight = self.product_id.weight * self.qty

    @api.one
    @api.depends('product_id', 'product_id.weight_net', 'qty')
    def _calculate_total_weight_net(self):
        self.total_weight_net = self.product_id.weight_net * self.qty

    @api.one
    @api.depends('product_id', 'product_id.volume', 'qty')
    def _calculate_total_volume(self):
        self.total_volume = self.product_id.volume * self.qty

    weight = fields.Float(string='Weight', related="product_id.weight")
    weight_net = fields.Float(
        string='Net Weight', related="product_id.weight_net")
    volume = fields.Float(
        string='Volume', related="product_id.volume")
    total_weight = fields.Float(
        string='Total weight', compute='_calculate_total_weight', store=True)
    total_weight_net = fields.Float(
        string='Total Net weight', compute='_calculate_total_weight_net',
        store=True)
    total_volume = fields.Float(
        string='Total Volume', compute='_calculate_total_volume', store=True)

    @api.one
    @api.onchange('product_id', 'qty')
    def onchange_total_weight(self):
        self.total_weight = self.product_id.weight * self.qty

    @api.one
    @api.onchange('product_id', 'qty')
    def onchange_total_weight_net(self):
        self.total_weight_net = self.product_id.weight_net * self.qty


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    @api.one
    @api.depends('quant_ids', 'quant_ids.total_weight')
    def _calculate_total_weight(self):
        self.total_weight = sum(x.total_weight for x in self.quant_ids)

    @api.one
    @api.depends('quant_ids', 'quant_ids.total_weight_net')
    def _calculate_total_weight_net(self):
        self.total_weight_net = sum(x.total_weight_net for x in self.quant_ids)

    @api.one
    @api.depends('total_weight', 'empty_weight', 'quant_ids.total_weight',
                 'children_ids', 'children_ids.total_weight',
                 'children_ids.empty_weight')
    def _calculate_total_estim_weight(self):
        self.total_estim_weight = (
            self.total_weight + self.empty_weight +
            sum(x.total_weight + x.empty_weight for x in self.children_ids))
        self.real_weight = self.total_estim_weight

    @api.one
    @api.depends('total_weight_net', 'empty_weight',
                 'quant_ids.total_weight_net', 'children_ids',
                 'children_ids.empty_weight', 'children_ids.total_weight_net')
    def _calculate_total_estim_weight_net(self):
        self.total_estim_weight_net = (
            self.total_weight_net + self.empty_weight +
            sum(x.total_weight_net + x.empty_weight for x in
                self.children_ids))

    @api.one
    @api.depends('quant_ids', 'quant_ids.total_volume')
    def _calculate_total_volume(self):
        self.total_volume = sum(x.total_volume for x in self.quant_ids)

    @api.one
    @api.depends('height', 'width', 'length')
    def _calculate_permitted_volume(self):
        self.permitted_volume = self.height * self.width * self.length

    @api.one
    @api.depends('total_volume', 'children_ids', 'children_ids.total_volume')
    def _calculate_tvolume_charge(self):
        self.tvolume_charge = (
            self.total_volume + sum(x.total_volume for x in self.children_ids))

    height = fields.Float(string='Height', help='The height of the package')
    width = fields.Float(string='Width', help='The width of the package')
    length = fields.Float(string='Length', help='The length of the package')
    empty_weight = fields.Float(string='Empty Package Weight')
    pickings = fields.Many2many(
        comodel_name='stock.picking',
        relation='rel_picking_package', column1='package_id',
        column2='picking_id', string='Pickings')
    total_weight = fields.Float(
        string='Total weight', compute='_calculate_total_weight', store=True)
    total_weight_net = fields.Float(
        string='Total Net weight', compute='_calculate_total_weight_net',
        store=True)
    total_volume = fields.Float(
        string='Total Volume', compute='_calculate_total_volume', store=True)
    real_weight = fields.Float(string='Real weight')
    total_estim_weight = fields.Float(
        string='Total estimated weight',
        compute='_calculate_total_estim_weight', store=True)
    total_estim_weight_net = fields.Float(
        string='Total estimated Net weight',
        compute='_calculate_total_estim_weight_net', store=True)
    permitted_volume = fields.Float(
        string='Permitted volume', compute='_calculate_permitted_volume',
        store=True)
    tvolume_charge = fields.Float(
        string='Total volume charge', compute='_calculate_tvolume_charge',
        store=True)

    @api.one
    @api.onchange('ul_id')
    def onchange_ul_id(self):
        self.height = self.ul_id.height
        self.width = self.ul_id.width
        self.length = self.ul_id.length
        self.empty_weight = self.ul_id.weight

    @api.one
    @api.onchange('total_weight', 'empty_weight', 'quant_ids', 'children_ids')
    @api.depends('total_weight', 'empty_weight', 'quant_ids.total_weight',
                 'children_ids', 'children_ids.total_weight',
                 'children_ids.empty_weight')
    def onchange_real_weight(self):
        self.real_weight = (
            self.total_weight + self.empty_weight +
            sum(x.total_weight + x.empty_weight for x in self.children_ids))
