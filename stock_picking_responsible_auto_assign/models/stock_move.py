# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self, force_qty=False):
        res = super()._action_assign(force_qty=force_qty)
        # Every reservation (button, scheduler, confirmation, backorder) ends
        # here, so this is the single place where a transfer becomes ready.
        self.picking_id.filtered(
            lambda p: p.state == "assigned"
            and p.picking_type_id.responsible_assign_mode == "ready"
        )._auto_assign_responsible()
        return res
