# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self, force_qty=False):
        # Flag the reservation pass so that _update_reserved_quantity can
        # enforce the "all or nothing per line" policy below. Skipped when
        # forcing a quantity, where the caller explicitly wants the move
        # reserved.
        records = self
        if not force_qty:
            records = self.with_context(_reservation_policy_enforce=True)
        return super(StockMove, records)._action_assign(force_qty=force_qty)

    def _update_reserved_quantity(
        self,
        need,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        # All-or-nothing per line: refuse a partial reservation from stock.
        #
        # We check availability up front with _get_reserve_quantity, which has
        # no side effect, and skip the reservation entirely when it is short.
        if (
            self.env.context.get("_reservation_policy_enforce")
            and self.picking_id.reservation_policy == "line"
            and not self.move_orig_ids
            and float_compare(
                need, 0, precision_rounding=self.product_id.uom_id.rounding
            )
            > 0
        ):
            available = (
                self.env["stock.quant"]
                .with_context(packaging_uom_id=self.packaging_uom_id)
                ._get_reserve_quantity(
                    self.product_id,
                    location_id,
                    need,
                    uom_id=self.product_uom,
                    lot_id=lot_id,
                    package_id=package_id,
                    owner_id=owner_id,
                    strict=strict,
                )
            )
            available_quantity = sum(quantity for _quant, quantity in available)
            if (
                float_compare(
                    available_quantity,
                    need,
                    precision_rounding=self.product_id.uom_id.rounding,
                )
                < 0
            ):
                return 0.0
        return super()._update_reserved_quantity(
            need,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
