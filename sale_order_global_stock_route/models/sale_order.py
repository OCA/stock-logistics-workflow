# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    route_id = fields.Many2one(
        comodel_name='stock.location.route',
        string='Route',
        domain=[('sale_selectable', '=', True)],
        help='When you change this field all the lines will be changed.'
             ' After use it you will be able to change each line.',
    )

    @api.onchange('route_id')
    def _onchange_route_id(self):
        for line in self.order_line:
            line.route_id = line.order_id.route_id

    def write(self, vals):
        res = super().write(vals)
        if 'route_id' in vals:
            lines = self.mapped('order_line').filtered(
                lambda l: l.route_id.id != vals['route_id'])
            lines.write({'route_id': vals['route_id']})
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def product_id_change(self):
        res = super().product_id_change()
        self.route_id = self.order_id.route_id
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('route_id', False):
                order = self.env['sale.order'].browse(vals['order_id'])
                vals['route_id'] = order.route_id.id
        return super().create(vals_list)
