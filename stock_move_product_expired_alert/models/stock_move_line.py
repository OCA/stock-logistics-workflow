# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

EXPIRY_FIELD_TO_ALERT = {
    "alert_date": "product_alert_date_expiry_alert",
    "removal_date": "product_removal_date_expiry_alert",
    "use_date": "product_use_date_expiry_alert",
    "expiration_date": "product_expiry_alert",
}


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    @property
    def has_expired_product(self):
        field_alert = self.picking_type_id.check_expired_product_alert
        if field_alert and getattr(self.lot_id, EXPIRY_FIELD_TO_ALERT.get(field_alert)):
            return True
        return False
