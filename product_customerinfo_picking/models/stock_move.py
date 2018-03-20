# -*- coding: utf-8 -*-
# Copyright 2013-2017 Agile Business Group sagl
#     (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    @api.depends('picking_id.partner_id', 'product_id',
                 'product_id.customer_ids.product_code')
    def _compute_product_customer_code(self):
        for move in self.filtered(lambda m: m.picking_id and
                                  m.picking_id.partner_id and
                                  m.product_tmpl_id.customer_ids):
            suppliers = \
                move.product_tmpl_id.customer_ids.filtered(
                    lambda m: move.picking_id.partner_id)
            if suppliers:
                move.product_customer_code = suppliers[0].product_code

    product_customer_code = fields.Char(
        compute='_compute_product_customer_code',
        string='Product Customer Code',
        size=64
    )
