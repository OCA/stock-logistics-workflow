# Copyright 2020 Carlos Dauden - Tecnativa
# Copyright 2020 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    owner_restriction = fields.Selection(
        [
            ("standard_behavior", "Standard behavior"),
            ("unassigned_owner", "Unassigned owner"),
            ("picking_partner", "Picking partner"),
        ],
        string="Owner restriction",
        default="standard_behavior",
    )
