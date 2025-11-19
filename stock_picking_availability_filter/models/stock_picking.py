# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare


class StockPicking(models.Model):
    _inherit = "stock.picking"

    products_availability = fields.Char(search="_search_products_availability")

    @api.model
    def _search_products_availability(self, operator, value):
        if operator not in ("=", "!=") or not value:
            return []
        domain = [
            ("state", "in", ("waiting", "confirmed", "assigned")),
            ("picking_type_code", "=", "outgoing"),
        ]
        pickings = self.search(domain)
        if value == "available":
            picking_ids = pickings.filtered(
                lambda sp: value == sp.products_availability_state
            )
        elif value == "expected":
            picking_ids = pickings.filtered(
                lambda sp: sp.products_availability_state in ["expected", "late"]
                and not any(
                    float_compare(
                        move.forecast_availability,
                        0 if move.state == "draft" else move.product_qty,
                        precision_rounding=move.product_id.uom_id.rounding,
                    )
                    == -1
                    for move in sp.move_ids
                )
            )
        elif value == "late":
            picking_ids = pickings.filtered(
                lambda sp: sp.products_availability_state == "late"
                and any(
                    float_compare(
                        move.forecast_availability,
                        0 if move.state == "draft" else move.product_qty,
                        precision_rounding=move.product_id.uom_id.rounding,
                    )
                    == -1
                    for move in sp.move_ids
                )
            )
        else:
            return []
        # Restore user language
        return [("id", "in" if operator == "=" else "not in", picking_ids.ids)]
