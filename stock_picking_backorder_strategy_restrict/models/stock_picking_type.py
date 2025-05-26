from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    create_backorder = fields.Selection(
        selection_add=[("restrict", "Restrict")],
        ondelete={"restrict": "set default"},
    )
