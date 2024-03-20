# Copyright 2024 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _should_exclude_for_valuation(self):
        self.ensure_one()
        if self.restrict_partner_id.value_owner_inventory:
            return False
        return super()._should_exclude_for_valuation()
