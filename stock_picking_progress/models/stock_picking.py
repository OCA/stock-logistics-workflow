# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    progress = fields.Float(compute="_compute_progress", store=True, aggregator="avg")

    @api.depends("state", "move_ids.progress")
    def _compute_progress(self):
        for picking in self:
            if picking.state == "done" or not (
                moves_progress := picking.move_ids.mapped("progress")
            ):
                picking.progress = 100
            else:
                picking.progress = sum(moves_progress) / len(moves_progress)
