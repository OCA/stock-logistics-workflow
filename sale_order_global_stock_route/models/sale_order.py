# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from lxml import etree


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

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """The purpose of this is to write a context on "order_line" field
         respecting other contexts on this field.
         There is a PR (https://github.com/odoo/odoo/pull/26607) to odoo for
         avoiding this. If merged, remove this method and add the attribute
         in the field.
         """
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu,
        )
        if view_type == 'form':
            order_xml = etree.XML(res['arch'])
            order_line_fields = order_xml.xpath("//field[@name='order_line']")
            if order_line_fields:
                order_line_field = order_line_fields[0]
                context = order_line_field.attrib.get("context", "{}").replace(
                    "{", "{'default_route_id': route_id, ", 1,
                )
                order_line_field.attrib['context'] = context
                res['arch'] = etree.tostring(order_xml)
        return res
