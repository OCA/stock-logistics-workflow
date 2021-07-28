# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    use_manual_lot_selection = fields.Boolean(default=False)
