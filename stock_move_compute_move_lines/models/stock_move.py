# Copyright 2016 Cyril Gaudin, Camptocamp SA
# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    has_move_lines = fields.Boolean(compute="_compute_has_move_lines")

    @api.depends("move_line_ids")
    def _compute_has_move_lines(self):
        for move in self:
            move.has_move_lines = bool(move.move_line_ids)
