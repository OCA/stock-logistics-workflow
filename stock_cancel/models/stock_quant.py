# -*- coding: utf-8 -*-
# Copyright 2012 Andrea Cometa
# Copyright 2013 Agile Business Group sagl
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, exceptions, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    def _revert(self):
        for quant in self:
            previous_move = quant.history_ids[-1]
            if len(previous_move.linked_move_operation_ids) != 1:
                raise exceptions.ValidationError(
                    _('Cannot cancel a picking with multiple operations'))
            linked_operation = previous_move.linked_move_operation_ids[0]
            previous_location = linked_operation.operation_id.location_id
            quant.location_id = previous_location.id
            quant.write({'history_ids': [(3, quant.history_ids[-1].id)]})
