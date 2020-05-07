# Copyright 2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    allow_stock_picking_move_done_manual = fields.Boolean(
        string='Allow to complete individual lines in a picking'
    )
