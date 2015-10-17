# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Vauxoo
#    Author: Moisés Lopez, Osval Reyes
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
from openerp import api, fields, models


class StockProductionLot(models.Model):

    """
    Adds information about lot last location using quants data
    and avoid creation of duplicated serial numbers
    """
    _inherit = 'stock.production.lot'

    last_location_id = fields.Many2one(
        'stock.location',
        string="Last location",
        compute='_get_last_location_id',
        store=True)
    ref = fields.Char('Internal Reference',
                      help="Internal reference number"
                           " in this case it"
                           " is same of manufacturer's"
                           " serial number",
                      related="name", store=True, readonly=True)

    @api.multi
    @api.depends('quant_ids')
    def _get_last_location_id(self):
        for prodlot_id in self:
            last_quant_data = self.env['stock.quant'].search_read(
                [('id', 'in', prodlot_id.quant_ids.ids)],
                ['location_id'],
                order='in_date DESC, id DESC',
                limit=1)

            prodlot_id.last_location_id = last_quant_data and \
                last_quant_data[0]['location_id'][0] or False
