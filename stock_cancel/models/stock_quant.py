# -*- coding: utf-8 -*-
# Copyright 2012 Andrea Cometa
# Copyright 2013 Agile Business Group sagl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    def _revert(self, previous_move):
        previous_location = previous_move.location_id
        for quant in self.sudo():
            if len(previous_move.linked_move_operation_ids) != 1:
                raise exceptions.ValidationError(
                    _('Cannot cancel a picking with multiple operations'))
            quant.location_id = previous_location.id
            quant.write({'history_ids': [(3, previous_move.id)]})
