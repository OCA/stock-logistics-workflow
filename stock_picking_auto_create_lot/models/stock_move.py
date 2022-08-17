# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


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
            lambda m: m.picking_type_id.auto_create_lot and m.product_id.auto_create_lot
        )
        for move in moves_not_display:
            move.display_assign_serial = False
        return
