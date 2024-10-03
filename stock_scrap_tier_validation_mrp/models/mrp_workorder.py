# Copyright 2024 360ERP (<https://www.360erp.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def button_scrap(self):
        """Fix compatibility with stock_scrap_tier_validation"""
        action = super().button_scrap()
        action.pop("target")
        return action
