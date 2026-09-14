# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    restrict_reusable_package_in_destination = fields.Boolean(
        help="Check this if you want to restrict the filling of "
        "the destination package field."
    )
    log_warning_reusable_package_in_destination = fields.Boolean(
        help="Check this if you want to log a warning when users "
        "fill in the destination package field in movements."
    )
