# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    suggest_destination = fields.Boolean(
        help="Check this is in order to suggest the final destination of operations." ""
    )
    suggest_destination_partner = fields.Boolean(
        help="Check this if you want to suggest destination locations with pending moves"
        "with the same partner",
    )
    suggest_destination_additional_domain = fields.Char(
        help="Set a particular domain to suggest destination locations."
    )
