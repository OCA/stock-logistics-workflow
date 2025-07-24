# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020-2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        relation="sale_order_stock_picking_rel",
        column1="order_id",
        column2="picking_id",
        string="Transfers",
        copy=False,
    )

    def _action_cancel(self):
        for sale_order in self:
            # change the context so we can intercept this in StockPicking.action_cancel
            proc_groups = sale_order.order_line._get_procurement_group()
            super(
                SaleOrder,
                sale_order.with_context(cancel_sale_group_ids=proc_groups.ids),
            )._action_cancel()
        return True

    def get_name_for_delivery_line(self):
        """Get the name for the sale order displayed on the delivery note"""
        self.ensure_one()
        if self.client_order_ref:
            return self.name + " - " + self.client_order_ref
        else:
            return self.name
