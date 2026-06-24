# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.fields import Domain


class StockMove(models.Model):
    _inherit = "stock.move"

    def _key_assign_picking(self):
        # Keep moves whose sale order carries a different reservation policy in
        # separate transfers, so a transfer never mixes reservation policies
        # (its computed reservation_policy then stays unambiguous).
        return super()._key_assign_picking() + (
            self.sale_line_id.order_id.reservation_policy,
        )

    def _search_picking_for_assignation_domain(self):
        # Do not attach the move to an existing transfer that carries a
        # different reservation policy.
        domain = super()._search_picking_for_assignation_domain()
        policy = self.sale_line_id.order_id.reservation_policy
        if policy:
            domain = Domain.AND([domain, [("reservation_policy", "=", policy)]])
        return domain
