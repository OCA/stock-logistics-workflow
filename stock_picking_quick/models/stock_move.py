from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_add_from_catalog_picking(self):
        picking = self.env["stock.picking"].browse(self.env.context.get("picking_id"))

        if not picking:
            return False

        return picking.action_add_from_catalog()

    def _get_product_catalog_lines_data(self, parent_record, **kwargs):
        self.ensure_one()

        return {
            "quantity": self.product_uom_qty,
            "price": self.product_id.standard_price,
        }
