# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.one
    @api.depends('group_id', 'sale_id', 'sale_id.client_order_ref')
    def _calculate_client_order_ref(self):
        sale_obj = self.env['sale.order']
        self.client_order_ref = ''
        if self.group_id:
            cond = [('procurement_group_id', '=', self.group_id.id)]
            sale = sale_obj.search(cond, limit=1)
            self.client_order_ref = sale.client_order_ref

    client_order_ref = fields.Char(
        string="Sale Reference/Description",
        compute="_calculate_client_order_ref", store=True)
