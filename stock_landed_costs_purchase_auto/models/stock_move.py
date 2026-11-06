# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_cancel(self):
        # purchase cancels its moves directly, without going through
        # stock.picking.action_cancel, so the landed cost of a transfer
        # cancelled that way would stay in draft forever
        pickings = self.picking_id
        res = super()._action_cancel()
        pickings._cancel_orphan_landed_costs()
        return res
