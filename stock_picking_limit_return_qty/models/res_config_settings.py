from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    stock_picking_limit_return_qty = fields.Boolean(
        "Stock Picking Return Quantity Limit",
        config_parameter="stock_picking_limit_return_qty.stock_picking_limit_return_qty",
    )
