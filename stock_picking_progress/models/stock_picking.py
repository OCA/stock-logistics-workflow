# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    progress = fields.Float(
        compute="_compute_progress", store=True, group_operator="avg"
    )

    @api.depends("move_line_ids", "move_line_ids.progress")
    def _compute_progress(self):
        for record in self:
            if record.state == "done":
                record.progress = 100
                continue
            lines_progress = record.move_line_ids.mapped("progress")
            # Avoid dividing by 0
            if lines_progress:
                record.progress = sum(lines_progress) / len(lines_progress)
            else:
                record.progress = 0
