# Copyright 2013 - 2021 Agile Business Group sagl (<https://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.depends(
        "picking_id.partner_id",
        "product_id",
        "product_id.customer_ids.product_code",
        "product_id.customer_ids.product_name",
    )
    def _compute_product_customer_code(self):
        for move in self:
            product_customer_code = False
            product_customer_name = False
            if (
                move.picking_id
                and move.picking_id.partner_id
                and move.product_tmpl_id.customer_ids
            ):
                customer = fields.first(
                    move.product_tmpl_id.customer_ids.filtered(
                        lambda m, mo=move: m.partner_id == mo.picking_id.partner_id
                    )
                )
                product_customer_code = customer.product_code
                product_customer_name = customer.product_name
            move.product_customer_code = product_customer_code
            move.product_customer_name = product_customer_name

    product_customer_code = fields.Char(
        compute="_compute_product_customer_code",
    )
    product_customer_name = fields.Char(
        compute="_compute_product_customer_code",
    )
