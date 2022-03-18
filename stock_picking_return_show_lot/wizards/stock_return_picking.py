# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockReturnPicking(models.TransientModel):

    _inherit = "stock.return.picking.line"

    lot_ids = fields.Many2many(
        comodel_name="stock.production.lot", related="move_id.lot_ids"
    )
