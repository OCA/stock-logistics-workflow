# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    variable_quantity = fields.Boolean(
        help="Adjust chained moves to match the quantity done when validating "
        "this operation type.",
    )
