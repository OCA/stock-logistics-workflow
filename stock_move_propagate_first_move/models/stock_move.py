# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    first_move_id = fields.Many2one(
        comodel_name="stock.move",
        string="First Move",
        readonly=True,
        help="The original move which generated this one.",
    )
    first_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Original Operation Type",
        related="first_move_id.picking_type_id",
        store=True,
        help="Picking type of the original move which generated this one.",
    )

    def _is_inside_a_chain(self) -> bool:
        return bool(self.move_dest_ids or self.move_orig_ids)

    def _split(self, qty, restrict_partner_id=False):
        res = super()._split(qty, restrict_partner_id)
        self_first_move_from_chain = (
            not self.first_move_id and self._is_inside_a_chain()
        )
        if self_first_move_from_chain:
            for vals in res:
                vals["_split_first_move_id"] = self.id

        return res

    @api.model_create_multi
    def create(self, vals_list):
        # Extract the tracking flag before calling super so it doesn't break standard create
        split_first_move_ids = {}
        for i, vals in enumerate(vals_list):
            if "_split_first_move_id" in vals:
                split_first_move_ids[i] = vals.pop("_split_first_move_id")

        moves = super().create(vals_list)

        # Update the upstream moves to point to the newly created backorder
        for i, move in enumerate(moves):
            split_first_move_id = split_first_move_ids.get(i)
            if not split_first_move_id:
                continue
            # Find all moves that were tied to the split first_move
            # and have not yet been completed or cancelled.
            moves_to_update = self.env["stock.move"].search(
                [
                    ("first_move_id", "=", split_first_move_id),
                    ("state", "not in", ("done", "cancel")),
                ]
            )
            if moves_to_update:
                moves_to_update.write({"first_move_id": move.id})

        return moves
