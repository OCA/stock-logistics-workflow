# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    from_putaway_final_location_id = fields.Many2one(
        comodel_name="stock.location", compute="_compute_from_putaway_final_location_id"
    )

    @api.depends("location_dest_id")
    def _compute_from_putaway_final_location_id(self):
        for move in self:
            move.from_putaway_final_location_id = move.product_id.with_context(
                warehouse_id=move.location_dest_id.warehouse_id
            ).default_putaway_location_id
