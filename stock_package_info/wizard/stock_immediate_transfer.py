# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2015 AvanzOsc
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    @api.multi
    def process(self):
        self.ensure_one()
        if self.pick_id.pack_operation_ids:
            self.pick_id.create_all_move_packages()
        return super(StockImmediateTransfer, self).process()
