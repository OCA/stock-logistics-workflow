from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    group_pickings_by_release_blocked = fields.Boolean(
        "Group pickings by release blocked",
        help="If `Group pickings` is enabled they will be grouped by release blocked too.",
    )
