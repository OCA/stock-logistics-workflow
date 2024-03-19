# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    batch_id = fields.Many2one(
        comodel_name="stock.picking.batch",
        related="picking_id.batch_id",
        store=True,
    )
