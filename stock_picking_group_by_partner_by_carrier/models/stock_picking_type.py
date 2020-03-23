from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    group_pickings = fields.Boolean(
        "Group pickings",
        help="Group pickings for the same partner and carrier. "
        "Pickings with shipping policy set to "
        "'When all products are ready' are never grouped.",
    )
