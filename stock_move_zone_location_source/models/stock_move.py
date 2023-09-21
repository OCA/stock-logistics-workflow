# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    source_zone_location_ids = fields.Many2many(
        comodel_name="stock.location",
        compute="_compute_source_zone_location_ids",
        help="This represents the original source location zone in the flow from where"
        "this move comes from.",
    )

    def _find_source_zone_location_move(self, visited=None):
        # Find all the origin moves if we find the first picking type
        # that is considered as the the source one
        # WARNING: The first call should be done with a single recordset
        all_moves = self.filtered(
            "move_line_ids.location_id.zone_location_id.is_considered_as_source"
        )
        unvisited_moves = (self - visited) if visited else self
        for move in unvisited_moves:
            all_moves |= move.move_orig_ids._find_source_zone_location_move()
        return all_moves

    @api.depends("move_orig_ids")
    def _compute_source_zone_location_ids(self):
        for move in self:
            source_move = move._find_source_zone_location_move()
            move.source_zone_location_ids = (
                source_move.move_line_ids.location_id.zone_location_id
            )
