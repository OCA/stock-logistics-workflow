from odoo import fields, models


class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    # same standard field, just here to clarify the table and column names
    picking_ids = fields.Many2many(
        "stock.picking",
        "stock_landed_cost_stock_picking_rel",
        "stock_landed_cost_id",
        "stock_picking_id",
        string="Transfers",
        copy=False,
    )
