# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    progress = fields.Float(
        compute="_compute_progress", store=True, group_operator="avg"
    )

    @api.depends("move_lines", "move_lines.progress")
    def _compute_progress(self):
        for record in self:
            if record.state == "done":
                record.progress = 100
                continue
            moves_progress = record.move_lines.mapped("progress")
            # Avoid dividing by 0
            if moves_progress:
                record.progress = sum(moves_progress) / len(moves_progress)
            else:
                record.progress = 100
