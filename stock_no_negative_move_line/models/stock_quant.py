from odoo import api, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.constrains("product_id", "quantity")
    def check_negative_qty(self):
        if self.env.company.prevent_negative_quantity_on == "validation":
            super().check_negative_qty()
