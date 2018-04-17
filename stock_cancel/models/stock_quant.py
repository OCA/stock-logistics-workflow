# -*- coding: utf-8 -*-
# Copyright 2012 Andrea Cometa
# Copyright 2013 Agile Business Group sagl
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    def _revert(self):
        for quant in self:
            previous_move = quant.history_ids[-1]
            previous_location = previous_move.location_id
            quant.location_id = previous_location.id
            quant.write({'history_ids': [(3, quant.history_ids[-1].id)]})
