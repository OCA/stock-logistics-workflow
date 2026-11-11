# Copyright 2026 Carlos Dauden - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    owner_restriction = fields.Selection(related="picking_type_id.owner_restriction")
    restricted_owner_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_restricted_owner_id",
    )

    @api.depends(
        "move_id.restricted_owner_id",
        "picking_id.owner_id",
        "picking_id.partner_id",
    )
    def _compute_restricted_owner_id(self):
        for line in self:
            line.restricted_owner_id = (
                line.move_id.restricted_owner_id
                if line.move_id
                else line.picking_id.owner_id or line.picking_id.partner_id
            )
