# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "line.numbering.mixin"]

    _line_numbering_lines_field = "move_ids"
    _line_numbering_position_field = "position"

    def action_renumber_lines_positions(self):
        """Renumber the transfer's moves (UI action)."""
        self.ensure_one()
        return super().renumber_lines_positions()
