# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    sale_stock_picking_variable_qty = fields.Boolean(
        string="Variable Sale Quantity",
        help="Adjust the linked sale order line quantity to match the actual "
        "quantity done when validating this operation.",
    )
