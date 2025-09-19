from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        existing_pickings = self.mapped("order_id.picking_ids")
        res = super()._action_launch_stock_rule(
            previous_product_uom_qty=previous_product_uom_qty
        )
        if not self.env.context.get("keep_line_sequence"):
            new_pickings = self.mapped("order_id.picking_ids") - existing_pickings
            new_pickings._reset_sequence()
        return res
