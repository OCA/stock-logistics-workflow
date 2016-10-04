# -*- coding: utf-8 -*-
# Copyright 2015-2016 Agile Business Group (<http://www.agilebg.com>)
# Copyright 2016 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api
from ..wizards.stock_transfer_details import check_date


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def action_done(self):
        # do actual processing
        result = super(StockMove, self).action_done()
        # overwrite date field where applicable
        for move in self:
            if move.linked_move_operation_ids:
                operation = move.linked_move_operation_ids[0]
                move.date = operation.operation_id.date
                if move.quant_ids:
                    check_date(move.date)
                    move.quant_ids.sudo().write({'in_date': move.date})
        pickings = self.mapped('picking_id').filtered(
            lambda r: r.state == 'done')
        for picking in pickings:
            # set date_done as the youngest date among the moves
            dates = picking.mapped('move_lines.date')
            picking.write({'date_done': max(dates)})
        return result
