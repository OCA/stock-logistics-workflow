# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    propagate_variable_qty = fields.Boolean(
        string="Propagate variable quantities",
        help="Update chained destination moves with the quantity actually processed.",
    )
