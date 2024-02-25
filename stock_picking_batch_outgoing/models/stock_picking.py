# Copyright 2024 Tecnativa - Sergio Teruel
# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    batch_outgoing_id = fields.Many2one(
        comodel_name="stock.picking.batch",
        related="move_lines.first_move_id.first_move_id.picking_id.batch_id",
        string="Batch Outgoing",
        store=True,
    )
