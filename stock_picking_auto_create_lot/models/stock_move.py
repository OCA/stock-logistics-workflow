# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.tools.float_utils import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.depends(
        "has_tracking",
        "picking_type_id.auto_create_lot",
        "product_id.auto_create_lot",
        "picking_type_id.use_existing_lots",
        "state",
    )
    def _compute_display_assign_serial(self):
        super()._compute_display_assign_serial()
        moves_not_display = self.filtered(
            lambda m: m.picking_type_id.auto_create_lot
            and (m.product_id.auto_create_lot or m.product_id.categ_id.auto_create_lot)
        )
        for move in moves_not_display:
            move.display_assign_serial = False
        return

    def _set_quantity_done_prepare_vals(self, qty):
        if (
            self.state in ("partially_available", "assigned")
            and self.product_id.tracking != "none"
            and self.picking_type_id.auto_create_lot
            and (
                self.product_id.auto_create_lot
                or self.product_id.categ_id.auto_create_lot
            )
            and self.move_line_ids
        ):
            total_qty = self.product_uom._compute_quantity(
                qty, self.product_uom, round=False
            )
            if (
                float_compare(
                    total_qty, 0, precision_rounding=self.product_uom.rounding
                )
                > 0
            ):
                first_ml = self.move_line_ids[0]
                first_ml_qty = self.product_uom._compute_quantity(
                    total_qty, first_ml.product_uom_id, round=False
                )
                first_ml.quantity = first_ml_qty
        return super()._set_quantity_done_prepare_vals(qty)
