from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    lot_info = fields.Char("Lot/Serial Number Info")
    lot_info_usage = fields.Selection(
        related="product_id.product_tmpl_id.lot_info_usage"
    )
