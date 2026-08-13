# Copyright 2024 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_lot_sequence(self) -> str:
        """Return the next lot/serial name for this move line.

        For SKU-based products:
          - uses a dedicated per-product ir.sequence
            (prefix '<SKU>-', padding from settings).
        Fallback:
          - uses default Odoo sequence 'stock.lot.serial'
            when SKU-based is not applicable or per-product
            sequence is not available.

        :return: Generated lot/serial name.
        :rtype: str
        """
        self.ensure_one()
        product = self.product_id

        if (
            product.product_tmpl_id.auto_create_lot_option != "sku_based"
            or not product.default_code
        ):
            return self.env["ir.sequence"].next_by_code("stock.lot.serial")

        seq = product.auto_create_lot_sequence_id
        if not seq:
            # Sequence should be prepared by product create/write or by picking flow.
            return self.env["ir.sequence"].next_by_code("stock.lot.serial")

        return seq.sudo().with_company(self.company_id).next_by_id()
