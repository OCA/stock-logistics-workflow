# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _create_backorder(self, backorder_moves=None):
        """Create new landed cost to backorder.
        We need to use sudo() because only Inventory > Administrator have
        permissions on stock.landed.cost."""
        res = super()._create_backorder(backorder_moves)
        if res and res.purchase_id.sudo().landed_cost_ids:
            res.purchase_id._create_picking_with_stock_landed_cost(res)
        return res

    def _cancel_orphan_landed_costs(self):
        """Cancel the draft landed costs left behind by a cancelled transfer."""
        costs = (
            self.env["stock.landed.cost"]
            .sudo()
            .search([("picking_ids", "in", self.ids), ("state", "=", "draft")])
        )
        costs.filtered(
            lambda cost: all(picking.state == "cancel" for picking in cost.picking_ids)
        ).button_cancel()
