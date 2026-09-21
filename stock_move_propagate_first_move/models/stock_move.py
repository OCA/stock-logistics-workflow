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
        index="btree_not_null",
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
        split_first_move_id_by_move_index = {}
        for i, vals in enumerate(vals_list):
            if "_split_first_move_id" in vals:
                split_first_move_id_by_move_index[i] = vals.pop("_split_first_move_id")

        moves = super().create(vals_list)

        self._propagate_first_move_after_create(
            split_first_move_id_by_move_index, moves
        )

        return moves

    def _propagate_first_move_after_create(
        self, split_first_move_id_by_move_index, moves
    ):
        """Propagate the new first_move_id to upstream moves created from a split."""
        if not split_first_move_id_by_move_index:
            return

        split_first_move_ids = [
            fm_id for fm_id in split_first_move_id_by_move_index.values() if fm_id
        ]

        # Find all ongoing moves tied to any of the split first_moves
        groups = self.env["stock.move"].read_group(
            domain=[
                ("first_move_id", "in", split_first_move_ids),
                ("state", "not in", ("done", "cancel")),
            ],
            fields=[
                "first_move_id",
                "move_ids:array_agg(id)",
            ],
            groupby=["first_move_id"],
        )
        grouped_moves_to_update = {
            group["first_move_id"][0]: self.env["stock.move"].browse(group["move_ids"])
            for group in groups
        }

        # Replace old first move with new one for each group
        for i, move in enumerate(moves):
            split_first_move_id = split_first_move_id_by_move_index.get(i)
            if split_first_move_id and split_first_move_id in grouped_moves_to_update:
                grouped_moves_to_update[split_first_move_id].write(
                    {"first_move_id": move.id}
                )
