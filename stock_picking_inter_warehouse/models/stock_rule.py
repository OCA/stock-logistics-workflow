# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    inter_warehouse_src_id = fields.Many2one(
        "stock.warehouse", "Inter Warehouse Source"
    )

    def _run_push(self, move):
        # Do not execute _run_push if the picking type
        # is an inter_warehouse_transfer, and it has not been validated
        if not (
            move.picking_id.type_inter_warehouse_transfer
            and move.picking_id.state != "done"
        ):
            return super()._run_push(move)

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        res = super()._push_prepare_move_copy_values(move_to_copy, new_date)
        if move_to_copy.picking_type_id.inter_warehouse_transfer:
            partner_id = (
                move_to_copy.picking_type_id.warehouse_id.receipt_picking_partner_id
            )
            res.update(
                {
                    "partner_id": partner_id.id,
                    "inter_warehouse_picking_id": move_to_copy.picking_id.id,
                }
            )
        return res
