from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    picking_ids = fields.Many2many("stock.picking", string="Transfers", copy=False)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_group_vals(self):
        vals = super()._prepare_procurement_group_vals()
        vals["carrier_id"] = self.order_id.carrier_id.id
        return vals
