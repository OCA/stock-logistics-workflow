# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .stock_picking_type import RESERVATION_POLICY_HELP, RESERVATION_POLICY_SELECTION


class StockPicking(models.Model):
    _inherit = "stock.picking"

    reservation_policy = fields.Selection(
        selection=RESERVATION_POLICY_SELECTION,
        compute="_compute_reservation_policy",
        store=True,
        required=True,
        readonly=False,
        precompute=True,
        help=RESERVATION_POLICY_HELP,
    )

    @api.depends("picking_type_id")
    def _compute_reservation_policy(self):
        # Default from the operation type. Mirrors how the picking's shipping
        # policy (move_type) defaults from its operation type.
        for picking in self:
            picking.reservation_policy = (
                picking.picking_type_id.reservation_policy or "direct"
            )
