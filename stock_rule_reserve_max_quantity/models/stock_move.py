# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _update_reserved_quantity(
        self,
        need,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        self.ensure_one()
        if self.rule_id.reserve_max_quantity:
            orig_done_product_uom_qty = 0.0
            for orig_move in self.move_orig_ids:
                # Convert origin to the product UoM of the current move.
                orig_done_product_uom_qty += orig_move.product_uom._compute_quantity(
                    orig_move.quantity,
                    self.product_uom,
                )
            real_need = orig_done_product_uom_qty - sum(
                self.move_line_ids.mapped("quantity_product_uom")
            )
            if (
                float_compare(need, 0.0, precision_rounding=self.product_uom.rounding)
                > 0
            ):
                need = real_need
        return super()._update_reserved_quantity(
            need,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
