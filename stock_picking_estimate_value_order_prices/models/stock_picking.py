from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _compute_product_price(self):
        super()._compute_product_price()
        for move in self:
            if move.picking_id.sale_id:
                move.product_price = (
                    (
                        move.sale_line_id.price_subtotal
                        / move.sale_line_id.product_uom_qty
                    )
                    if move.sale_line_id.product_uom_qty
                    else 0
                )
            elif move.picking_id.purchase_id:
                move.product_price = (
                    (
                        move.purchase_line_id.price_subtotal
                        / move.purchase_line_id.product_uom_qty
                    )
                    if move.purchase_line_id.product_uom_qty
                    else 0
                )
