# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _create_backorder(self):
        """Create new landed cost to backorder.
        We need to use sudo() because only Inventory > Administrator have
        permissions on stock.landed.cost."""
        res = super()._create_backorder()
        if res and res.purchase_id.sudo().landed_cost_ids:
            res.purchase_id._create_picking_with_stock_landed_cost(res)
        return res
