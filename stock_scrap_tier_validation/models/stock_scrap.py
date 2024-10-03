# Copyright 2023 Jarsa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockScrap(models.Model):
    _name = "stock.scrap"
    _inherit = ["stock.scrap", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["done"]

    _tier_validation_manual_config = False

    def _get_requested_notification_subtype(self):
        return "stock_scrap_tier_validation.sale_order_tier_validation_requested"

    def _get_accepted_notification_subtype(self):
        return "stock_scrap_tier_validation.sale_order_tier_validation_accepted"

    def _get_rejected_notification_subtype(self):
        return "stock_scrap_tier_validation.sale_order_tier_validation_rejected"

    @api.model
    def _get_under_validation_exceptions(self):
        res = super()._get_under_validation_exceptions()
        res.append("name")
        return res
