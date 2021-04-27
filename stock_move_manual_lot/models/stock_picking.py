# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    use_manual_lot_selection = fields.Boolean(
        related="picking_type_id.use_manual_lot_selection",
    )

    def button_validate(self):
        """Call the logic to reserve lots selected in field
        manual_lot_id. The result is an error if no manual lot
        is selected for products with tracking!=none"""
        self.mapped("move_line_ids")._reserve_manual_lot(
            {
                "manual_lot_id": True,
            }
        )
        return super().button_validate()
