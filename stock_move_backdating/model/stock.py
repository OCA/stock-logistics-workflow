# -*- coding: utf-8 -*-
# ©2015 Agile Business Group (<http://www.agilebg.com>)
# ©2015 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


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
                    move.quant_ids.sudo().write({'in_date': move.date})

        return result
