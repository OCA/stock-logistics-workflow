# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _selection_auto_create_lot_option(self):
        """Return possible auto lot/serial generation options.

        :return: List of (value, label) pairs for selection field.
        :rtype: list[tuple[str, str]]
        """
        return [
            ("odoo_sequence", self.env._("Odoo sequence")),
            ("sku_based", self.env._("SKU based")),
        ]

    auto_create_lot_option = fields.Selection(
        selection="_selection_auto_create_lot_option",
        help="Controls how lots/serial numbers are auto-generated for this product.",
    )

    def write(self, vals):
        res = super().write(vals)
        if "auto_create_lot_option" in vals:
            self.mapped("product_variant_ids")._auto_lot_sequence_sync_if_needed()
        return res
