# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    next_picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        compute="_compute_next_picking_ids",
    )
    next_picking_name = fields.Char(
        compute="_compute_next_picking_name",
    )

    @api.depends("move_dest_ids")
    def _compute_next_picking_ids(self):
        for move in self:
            move.next_picking_ids = move.move_dest_ids.picking_id

    @api.depends("next_picking_ids")
    def _compute_next_picking_name(self):
        for move in self:
            # Odoo will remove first() and recommend to use next(iter()) instead
            move.next_picking_name = (
                next(iter(move.next_picking_ids)).name if move.next_picking_ids else ""
            )
