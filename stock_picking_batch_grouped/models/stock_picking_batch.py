#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    grouped_line_ids = fields.One2many(
        comodel_name="stock.picking.batch.line",
        inverse_name="batch_id",
        compute="_compute_grouped_line_ids",
        store=True,
        readonly=False,
        string="Grouped Lines",
    )

    @api.depends(
        "move_line_ids",
    )
    def _compute_grouped_line_ids(self):
        for batch in self:
            move_lines = batch.move_line_ids
            grouped_lines_values = self.env[
                "stock.picking.batch.line"
            ].create_from_move_lines(move_lines)
            batch.grouped_line_ids = grouped_lines_values
