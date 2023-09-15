# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    inter_warehouse_transfer = fields.Boolean(string="Inter-Warehouse Transfer")
    disable_merge_picking_moves = fields.Boolean(
        string="Disable Merge Picking Moves",
        help="Force one reception picking for each delivery",
    )
