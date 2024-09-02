# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockReturnPickingLine(models.TransientModel):

    _inherit = "stock.return.picking.line"

    lot_id = fields.Many2one(
        "stock.lot",
        string="Lot/Serial Number",
        domain="[('product_id', '=', product_id)]",
    )
    lots_visible = fields.Boolean(compute="_compute_lots_visible")

    @api.depends("product_id.tracking")
    def _compute_lots_visible(self):
        for rec in self:
            rec.lots_visible = rec.product_id.tracking != "none"
