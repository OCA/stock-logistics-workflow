# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


class stock_move(models.Model):
    _inherit = "stock.move"

    @api.multi
    def action_done(self):
        # do actual processing
        result = super(stock_move, self).action_done()
        # overwrite date field where applicable
        for move in self:
            if move.linked_move_operation_ids:
                operation = move.linked_move_operation_ids[0]
                move.date = operation.operation_id.date
                if move.quant_ids:
                    move.quant_ids.sudo().write({'in_date': move.date})

        return result
