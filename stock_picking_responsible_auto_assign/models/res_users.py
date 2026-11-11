# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    picking_assign_available = fields.Boolean(
        string="Available for Picking Assignment",
        default=True,
        help="Uncheck it when the user is absent: the automatic assignment of "
        "transfers will skip this user until it is checked again.",
    )

    def write(self, vals):
        res = super().write(vals)
        if vals.get("picking_assign_available"):
            self.env["stock.picking.type"].sudo().search(
                [("responsible_user_ids", "in", self.ids)]
            )._assign_queued_pickings()
        return res
