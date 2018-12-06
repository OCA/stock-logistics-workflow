# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _cancel_remaining_quantities(self):
        to_cancel = self.filtered(lambda m: m.state not in ('done', 'cancel'))
        to_cancel._action_cancel()
