from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    default_move_type = fields.Selection(
        [("direct", "As soon as possible"), ("one", "When all products are ready")],
        "Default Shipping Policy",
        help="Default shipping policy for pickings of this operation type",
    )
