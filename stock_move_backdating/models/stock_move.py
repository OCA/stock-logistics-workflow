# -*- coding: utf-8 -*-
# Copyright 2015-2016 Agile Business Group (<http://www.agilebg.com>)
# Copyright 2016 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
# Copyright 2018 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from ..models.stock_pack_operation import check_date


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
                if operation.operation_id.date_backdating:
                    move.date = operation.operation_id.date_backdating
                    if move.quant_ids:
                        check_date(move.date)
                        move.quant_ids.sudo().write({'in_date': move.date})
        return result
