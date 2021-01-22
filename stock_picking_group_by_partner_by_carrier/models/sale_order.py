from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    picking_ids = fields.Many2many("stock.picking", string="Transfers", copy=False)

    def action_cancel(self):
        for sale_order in self:
            # change the context so we can intercept this in StockPicking.action_cancel
            super(
                SaleOrder, sale_order.with_context(cancel_sale_id=sale_order.id)
            ).action_cancel()

    def action_draft(self):
        res = super().action_draft()
        self.procurement_group_id = False
        return res

    def get_name_for_delivery_line(self):
        """Get the name for the sale order displayed on the delivery note"""
        self.ensure_one()
        if self.client_order_ref:
            return self.name + " - " + self.client_order_ref
        else:
            return self.name


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_group_vals(self):
        vals = super()._prepare_procurement_group_vals()
        if not vals.get("sale_ids") and vals.get("sale_id"):
            vals["sale_ids"] = [(6, 0, [vals["sale_id"]])]
        vals["carrier_id"] = self.order_id.carrier_id.id
        return vals
