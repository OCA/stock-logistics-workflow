# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.fields import Domain

from .stock_picking import BACKORDER_POLICY_HELP, BACKORDER_POLICY_SELECTION


class StockMove(models.Model):
    _inherit = "stock.move"

    backorder_policy = fields.Selection(
        selection=BACKORDER_POLICY_SELECTION,
        help=BACKORDER_POLICY_HELP,
    )

    def _prepare_procurement_values(self):
        # Carry the policy onto chained (upstream) procurements so it survives
        # multi-step delivery routes and make-to-order chains.
        values = super()._prepare_procurement_values()
        values["backorder_policy"] = self.backorder_policy
        return values

    def _get_new_picking_values(self):
        # Propagate the policy onto the picking the moves create. Moves grouped
        # into one picking share the same policy (see _key_assign_picking), so
        # the first move is representative.
        vals = super()._get_new_picking_values()
        vals["backorder_policy"] = self[:1].backorder_policy
        return vals

    def _prepare_merge_moves_distinct_fields(self):
        # Do not merge moves that carry a different policy.
        return super()._prepare_merge_moves_distinct_fields() + ["backorder_policy"]

    def _key_assign_picking(self):
        # Keep moves with different policies in separate pickings.
        return super()._key_assign_picking() + (self.backorder_policy,)

    def _search_picking_for_assignation_domain(self):
        # Do not attach a move to an existing picking with a different policy.
        domain = super()._search_picking_for_assignation_domain()
        return Domain(domain) & Domain("backorder_policy", "=", self.backorder_policy)
