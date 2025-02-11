# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    check_expired_product_alert = fields.Selection(
        selection=[
            ("alert_date", "Trigger an alert if alert date is expired"),
            ("removal_date", "Trigger an alert if removal date is expired"),
            ("use_date", "Trigger an alert if use date is expired"),
            ("expiration_date", "Trigger an alert if expiration date is expired"),
        ],
        help="Choose the field that will trigger an activity if an expired "
        "product is transferred.",
    )
