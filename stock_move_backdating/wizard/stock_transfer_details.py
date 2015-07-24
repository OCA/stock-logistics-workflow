# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Agile Business Group (<http://www.agilebg.com>)
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

from openerp import models, fields, api


class StockTransferDetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    date_backdating = fields.Datetime("Actual Movement Date")

    @api.onchange('date_backdating')
    def on_change_date_backdating(self):
        self.date = self.date_backdating
        # for link_move in self.packop_id.linked_move_operation_ids:
            # link_move.move_id.write({'date_backdating': self.date_backdating}
        # )
        # return {}
# class stock_transfer_details(models.TransientModel):
    # _inherit = 'stock.transfer_details'
#
    # @api.one
    # def do_detailed_transfer(self):
        # for wizard_line in self.item_ids:
            # date_backdating = wizard_line.date_backdating
            # wizard_line.move_lines.write({'date_backdating': date_backdating, })
        # return super(stock_partial_picking, self).do_partial(cr, uid, ids,
                                                             # context=context)