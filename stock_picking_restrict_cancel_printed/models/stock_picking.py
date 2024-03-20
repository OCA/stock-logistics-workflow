# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_cancel(self):
        for pick in self:
            if pick.printed:
                raise UserError(
                    _("You cannot cancel a transfer that is already printed.")
                )
        return super().action_cancel()
