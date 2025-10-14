# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"  # pylint: disable=consider-merging-classes-inherited

    def _planned_delivery_date(self):
        # Convert FakeDatetime to FakeDate
        date = super()._planned_delivery_date()
        return date.date() if date else date
