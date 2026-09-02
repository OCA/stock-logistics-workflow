# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.stock_picking_backorder_policy.models.stock_picking import (
    BACKORDER_POLICY_HELP,
    BACKORDER_POLICY_SELECTION,
)


class ResPartner(models.Model):
    _inherit = "res.partner"

    purchase_backorder_policy = fields.Selection(
        selection=BACKORDER_POLICY_SELECTION,
        tracking=True,
        help=BACKORDER_POLICY_HELP,
    )

    @api.model
    def _commercial_fields(self):
        # Propagate the backorder policy from the commercial entity to all of
        # its contacts.
        return super()._commercial_fields() + ["purchase_backorder_policy"]
