# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    def auto_assign_packaging(self):
        # IN V13 the logic is implemented into the _action_done method
        # We deine this method here to keep the same path to trigger the
        # auto_assign_packaging method
        # stock.move -> stock.pack.operation -> stock.quant.package
        # action_done in stock module sometimes delete a stock.pack.operation,
        # we have to check if it still exists before reading/writing on it
        for line in self.exists().filtered(lambda l: l.result_package_id):
            line.result_package_id.auto_assign_packaging()
