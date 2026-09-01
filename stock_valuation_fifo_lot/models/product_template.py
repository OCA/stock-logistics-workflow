# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def get_product_accounts(self, fiscal_pos=None):
        accounts = super().get_product_accounts(fiscal_pos=fiscal_pos)
        lot_revaluation_journal = self.env.context.get("lot_revaluation_journal")
        if lot_revaluation_journal:
            accounts.update({"stock_journal": lot_revaluation_journal})
        return accounts
