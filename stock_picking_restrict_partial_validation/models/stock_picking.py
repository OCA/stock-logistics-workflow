# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        self._check_restrict_partial_validation()
        return super().button_validate()

    def _check_restrict_partial_validation(self):
        for picking in self.filtered(
            lambda p: p.picking_type_id.restrict_partial_validation
        ):
            if picking.state != "assigned":
                raise UserError(
                    _(
                        "%(picking)s cannot be validated: this operation "
                        "type requires the transfer to be fully reserved "
                        "before it can be processed.",
                        picking=picking.name,
                    )
                )
            moves = picking.move_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
            )
            any_picked = any(move.picked for move in moves)
            for move in moves:
                picked_qty = (
                    move._get_picked_quantity() if any_picked else move.quantity
                )
                if (any_picked and move.product_uom_qty and not move.picked) or (
                    float_compare(
                        picked_qty,
                        move.product_uom_qty,
                        precision_rounding=move.product_uom.rounding,
                    )
                    < 0
                ):
                    raise UserError(
                        _(
                            "%(picking)s must be processed in full: partial "
                            "validation is not allowed on this operation "
                            "type (%(product)s: %(qty)s of %(demand)s).",
                            picking=picking.name,
                            product=move.product_id.display_name,
                            qty=picked_qty,
                            demand=move.product_uom_qty,
                        )
                    )
            picking._check_restrict_partial_validation_over_reservation(moves)

    def _check_restrict_partial_validation_over_reservation(self, moves):
        # Manually entered quantities reserve quants even when there is no
        # stock, leaving them over-reserved and the move Available. Block the
        # validation when the reservation is not backed by physical stock.
        self.ensure_one()
        quant_model = self.env["stock.quant"]
        for line in moves.move_line_ids:
            if line.move_id._should_bypass_reservation(line.location_id):
                continue
            available = quant_model._get_available_quantity(
                line.product_id,
                line.location_id,
                lot_id=line.lot_id,
                package_id=line.package_id,
                owner_id=line.owner_id,
                allow_negative=True,
            )
            if (
                float_compare(
                    available,
                    0,
                    precision_rounding=line.product_uom_id.rounding,
                )
                < 0
            ):
                raise UserError(
                    _(
                        "%(picking)s cannot be validated: %(product)s is "
                        "reserved beyond the stock physically available in "
                        "%(location)s. Correct the stock or the reservation "
                        "first.",
                        picking=self.name,
                        product=line.product_id.display_name,
                        location=line.location_id.display_name,
                    )
                )
