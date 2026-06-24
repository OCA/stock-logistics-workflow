# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.stock_picking_reservation_policy.models.stock_picking_type import (
    RESERVATION_POLICY_HELP,
    RESERVATION_POLICY_SELECTION,
)


class ResPartner(models.Model):
    _inherit = "res.partner"

    reservation_policy = fields.Selection(
        selection=RESERVATION_POLICY_SELECTION,
        required=True,
        default="direct",
        help=RESERVATION_POLICY_HELP,
    )

    @api.model
    def _commercial_fields(self):
        # Share the reservation policy between a company and its contacts
        # (delivery addresses, etc.).
        return super()._commercial_fields() + ["reservation_policy"]
