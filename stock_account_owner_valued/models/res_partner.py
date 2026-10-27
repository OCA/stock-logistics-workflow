# Copyright 2024 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    value_owner_inventory = fields.Boolean(
        help="If enabled, the inventory valuation will be calculated for this partner."
    )
