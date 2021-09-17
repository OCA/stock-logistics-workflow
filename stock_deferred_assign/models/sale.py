# Copyright 2021 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """ Inject context to filter pickings in action_assign method"""
        return super(
            SaleOrderLine, self.with_context(from_launch_stock_rule=True)
        )._action_launch_stock_rule(previous_product_uom_qty=previous_product_uom_qty)
