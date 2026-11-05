# Copyright 2013 - 2021 Agile Business Group sagl (<https://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    product_customer_code = fields.Char(
        compute="_compute_product_customer_code",
    )
    product_customer_name = fields.Char(
        compute="_compute_product_customer_code",
    )

    @api.depends("product_id", "picking_id.partner_id")
    def _compute_product_customer_code(self):
        for move in self:
            customerinfo = self.env["product.customerinfo"].browse()
            if move.product_id and move.picking_id.partner_id:
                customerinfo = move.product_id._select_customerinfo(
                    partner=move.picking_id.partner_id
                )
            move.product_customer_code = customerinfo.product_code or ""
            move.product_customer_name = customerinfo.product_name or ""
