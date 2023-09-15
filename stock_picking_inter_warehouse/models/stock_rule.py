# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    inter_warehouse_src_id = fields.Many2one(
        "stock.warehouse", "Inter Warehouse Source"
    )

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        res = super()._push_prepare_move_copy_values(move_to_copy, new_date)
        if move_to_copy.picking_type_id.inter_warehouse_transfer:
            partner_id = (
                move_to_copy.picking_type_id.warehouse_id.receipt_picking_partner_id
            )
            res.update({"partner_id": partner_id.id})
        return res
