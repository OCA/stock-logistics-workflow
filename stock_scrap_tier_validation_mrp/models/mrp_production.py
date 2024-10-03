# Copyright 2024 360ERP (<https://www.360erp.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def button_scrap(self):
        """Fix compatibility with stock_scrap_tier_validation.

        The way that super opens the scrap form in a popup window prevents
        the tier validation UI elements from being effective. The record is
        only saved when closing the popup. Given that it's only possible to
        check if the record needs validation after saving, the popup will
        always raise the 'validation required' error which blocks saving it.

        As a workaround, we open the unsaved scrap record in the main window
        so that it can be saved first and then be requested validation for
        in the usual way.
        """
        action = super().button_scrap()
        action.pop("target")
        return action
