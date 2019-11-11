# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _action_done(self):
        res = super()._action_done()
        for line in self.filtered(lambda l: l.result_package_id):
            line.result_package_id.auto_assign_packaging()
        return res
