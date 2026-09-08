# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models
from odoo.tools import float_compare


class StockBackorderConfirmation(models.TransientModel):
    _inherit = "stock.backorder.confirmation"

    backorder_confirmation_move_line_ids = fields.One2many(
        "stock.backorder.confirmation.move.line",
        "backorder_confirmation_id",
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if "backorder_confirmation_move_line_ids" in fields and res.get("pick_ids"):
            # default_get returns x2m values as [(6, 0, ids)]
            # because of webclient limitations
            pickings = self.env["stock.picking"].browse(res["pick_ids"][0][2])

            res["backorder_confirmation_move_line_ids"] = [
                (0, 0, {"move_id": move.id}) for move in pickings.move_ids
            ]

        return res

    def process(self):
        prec = self.env["decimal.precision"].precision_get("Product Unit")
        if not self.show_transfers and (
            any(
                float_compare(
                    wiz_line.qty_unprocessed,
                    wiz_line.qty_to_backorder,
                    precision_digits=prec,
                )
                != 0
                for wiz_line in self.backorder_confirmation_move_line_ids
            )
            or len(self.backorder_confirmation_move_line_ids)
            != len(self.pick_ids.move_ids)
        ):
            moves_qty_to_backorder = {
                wiz_line.move_id.id: wiz_line.qty_to_backorder
                for wiz_line in self.backorder_confirmation_move_line_ids
            }
            self = self.with_context(
                force_moves_qty_to_backorder=moves_qty_to_backorder
            )
        return super().process()
