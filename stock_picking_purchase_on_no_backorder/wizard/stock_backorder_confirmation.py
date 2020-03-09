# -*- coding: utf-8 -*-
# Copyright 2020 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    @api.one
    def _process(self, cancel_backorder=False):
        res = super(StockBackorderConfirmation, self)._process(
            cancel_backorder)
        if cancel_backorder:
            # convert cancelled backorder picking into a purchase order:
            self.pick_id.purchase_backorder()
        return res
