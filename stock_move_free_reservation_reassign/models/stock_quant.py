# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockQuant(models.Model):

    _inherit = "stock.quant"

    def _apply_inventory(self):
        if (
            not self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "stock_move_free_reservation_reassign."
                "reassign_stock_move_after_free_reservation",
                False,
            )
        ):
            return super()._apply_inventory()

        with self.env[
            "stock.move.line"
        ]._get_move_free_reservation_ids() as move_to_reassign_ids:
            res = super()._apply_inventory()
        if move_to_reassign_ids:
            self.env["stock.move"].browse(move_to_reassign_ids).with_context(
                inventory_mode=False
            )._action_assign()
        return res
