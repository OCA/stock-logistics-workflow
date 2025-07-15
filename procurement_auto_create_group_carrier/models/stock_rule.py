# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_auto_procurement_group_data(self, product):
        data = super()._prepare_auto_procurement_group_data(product=product)
        if self.partner_address_id.property_delivery_carrier_id:
            data["carrier_id"] = self.partner_address_id.property_delivery_carrier_id.id
        return data
