# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020-2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_group_vals(self):
        vals = super()._prepare_procurement_group_vals()
        vals["carrier_id"] = self.order_id.carrier_id.id
        return vals

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        self._align_procurement_group_carrier()
        return super()._action_launch_stock_rule(
            previous_product_uom_qty=previous_product_uom_qty
        )

    def _align_procurement_group_carrier(self):
        """Set the order carrier on a reused procurement group.

        A group created on a previous confirmation keeps the carrier of that
        time. When it is reused (e.g. the order was cancelled, set back to
        quotation with another carrier and confirmed again), new pickings
        would get the old carrier. Groups that still have open pickings are
        left untouched: their carrier follows the pickings.
        """
        picking_model = self.env["stock.picking"]
        for line in self:
            group = line._get_procurement_group()
            carrier = line.order_id.carrier_id
            if not group or group.carrier_id == carrier:
                continue
            has_open_pickings = picking_model.search_count(
                [
                    ("group_id", "=", group.id),
                    ("state", "not in", ("done", "cancel")),
                ],
                limit=1,
            )
            if not has_open_pickings:
                group.carrier_id = carrier
