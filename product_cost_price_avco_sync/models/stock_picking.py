# Copyright 2019 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_done(self):
        """ Avoid AVCO cost price recomputation when validating picking """
        return super(StockPicking, self.with_context(
            skip_avco_sync=True)).action_done()
