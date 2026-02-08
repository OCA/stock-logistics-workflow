# Copyright 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.constrains("quantity", "lot_id")
    def _check_partial_approved_qty(self):
        """Validate that total lot quantity in restricted locations
        doesn't exceed partial approved quantity."""
        # Allow bypass for specific operations (similar to stock_no_negative)
        if self.env.context.get("skip_partial_approved_qty_check"):
            return

        # Filter quants that need validation
        quants_to_check = self.filtered(
            lambda q: q.quantity > 0
            and q.lot_id
            and q.lot_id.partial_approved_qty > 0
            and not q.location_id.allow_locked
        )

        # Group by lot to avoid repeated calculations
        lots_to_validate = {}
        for quant in quants_to_check:
            lot_id = quant.lot_id.id
            if lot_id not in lots_to_validate:
                lots_to_validate[lot_id] = {
                    "lot": quant.lot_id,
                    "quants": self.env["stock.quant"],
                }
            lots_to_validate[lot_id]["quants"] |= quant

        # Validate each lot once
        for lot_data in lots_to_validate.values():
            lot = lot_data["lot"]
            quants = lot_data["quants"]

            # Calculate total usable quantity for this lot
            total_usable_qty = sum(
                quants.filtered(
                    lambda q: not q.location_id.allow_locked
                    and q.location_id.usage == "internal"
                ).mapped("quantity")
            )

            # Validate against partial approved quantity
            if total_usable_qty > lot.partial_approved_qty:
                # Find the first location causing the issue for error message
                problematic_quant = quants.filtered(
                    lambda q: not q.location_id.allow_locked
                    and q.location_id.usage == "internal"
                )[0]

                raise exceptions.ValidationError(
                    _(
                        "Cannot validate this stock operation because the total "
                        "quantity of lot '%(lot)s' (%(total).2f) in locations "
                        "that don't allow locked lots exceeds the partial "
                        "approved quantity (%(approved).2f).\n"
                        "Location: %(location)s\n"
                        "Move excess quantities to locations that allow locked lots "
                        "or increase the partial approved quantity.",
                        lot=lot.name,
                        total=total_usable_qty,
                        approved=lot.partial_approved_qty,
                        location=problematic_quant.location_id.complete_name,
                    )
                )
