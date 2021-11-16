# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockScrap(models.Model):

    _inherit = "stock.scrap"

    def mass_validate(self):
        if not self.env.context.get("active_ids"):
            return
        scraps = self.browse(self.env.context["active_ids"])
        for scrap in scraps:
            scrap.action_validate()
