from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    group_pickings_by_date = fields.Boolean(
        "Group pickings by date",
        help="If `Group pickings` is enabled they will be grouped by date too.",
    )
