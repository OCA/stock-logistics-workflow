from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_to_ship = fields.Float(
        compute="_compute_qty_to_ship", store=True, digits="Product Unit of Measure",
    )

    deliverable_rate = fields.Float(
        compute="_compute_deliverable_rate",
        store=False,
        digits="Sale order deliverable rate",
    )

    def _qty_to_ship(self):
        self.ensure_one()
        return self.product_uom_qty - self.qty_delivered

    @api.depends("product_uom_qty", "qty_delivered")
    def _compute_qty_to_ship(self):
        for rec in self:
            rec.qty_to_ship = rec._qty_to_ship()

    def _avg_rate(self):
        self.ensure_one()
        # max if product qty_available is negative
        return max(0, self.product_id.qty_available) / self.qty_to_ship

    @api.depends("product_id", "qty_delivered", "qty_to_ship")
    def _compute_deliverable_rate(self):
        for rec in self:
            if rec.product_id.type == "product" and rec.qty_to_ship > 0:
                rec.deliverable_rate = min(100, rec._avg_rate() * 100)
            else:
                rec.deliverable_rate = 0
