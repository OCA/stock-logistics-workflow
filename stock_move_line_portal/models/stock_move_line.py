# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMoveLine(models.Model):
    _name = "stock.move.line"
    _inherit = ["portal.mixin", "stock.move.line"]

    def _compute_access_url(self):
        super()._compute_access_url()
        for line in self:
            line.access_url = f"/my/move_operations/{line.id}"
        return
