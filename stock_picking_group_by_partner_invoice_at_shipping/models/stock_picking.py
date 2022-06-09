# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _invoice_at_shipping(self):
        self.ensure_one()
        return self.picking_type_code == "outgoing" and "at_shipping" in self.mapped(
            "sale_ids.partner_invoice_id.invoicing_mode"
        )

    def _get_sales_order_to_invoice(self):
        res = super()._get_sales_order_to_invoice()
        return res.filtered(
            lambda r: r.partner_invoice_id.invoicing_mode == "at_shipping"
        )
