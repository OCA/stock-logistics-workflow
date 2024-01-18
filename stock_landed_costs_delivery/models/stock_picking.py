# Copyright 2023-2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.tools import config


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _add_delivery_cost_to_po(self):
        """We add the context to identify in _create_delivery_line() method the picking."""
        self.ensure_one()
        self = self.with_context(from_picking=self)
        return super()._add_delivery_cost_to_po()

    def _action_done(self):
        """Validate Landed costs linked to the purchase and picking."""
        res = super()._action_done()
        if not config["test_enable"] or self.env.context.get(
            "test_stock_landed_costs_delivery"
        ):
            for item in self:
                landed_cost = item.purchase_id.sudo().landed_cost_ids.filtered(
                    lambda x: item in x.picking_ids
                    and x.state == "draft"
                    and x.cost_lines
                )
                if landed_cost:
                    landed_cost.button_validate()
        return res
