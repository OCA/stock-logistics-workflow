# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 AKRETION
#    @author Chafique Delli <chafique.delli@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.one
    @api.depends('company_id', 'company_id.warning_time', 'min_date')
    def compute_start_warning_date(self):
        if self.min_date:
            company = self.company_id
            warning_time = company.warning_time
            min_date_dt = fields.Datetime.from_string(self.min_date)
            start_warning_date = min_date_dt - relativedelta(
                days=warning_time or 0.0)
            self.start_warning_date = fields.Date.to_string(start_warning_date)

    start_warning_date = fields.Date(
        string='Start Warning Date',
        compute='compute_start_warning_date',
        readonly=True, store=True)


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    @api.one
    def _get_picking_count_late_soon(self):
        picking_obj = self.env['stock.picking']
        time_dt = fields.Datetime.context_timestamp(
            self, timestamp=datetime.datetime.now())
        time_str = fields.Date.to_string(time_dt)
        domains = {
            'count_picking_late_soon': [
                ('start_warning_date', '<=', time_str),
                ('min_date', '>', time_str),
                ('state', 'in', ('assigned',
                                 'waiting',
                                 'confirmed',
                                 'partially_available'))
            ]
        }
        data = picking_obj.read_group(
            domains['count_picking_late_soon'],
            ['picking_type_id'],
            ['picking_type_id']
        )
        count = dict(map(lambda x: (
            x['picking_type_id'] and x['picking_type_id'][0],
            x['picking_type_id_count']), data)
        )
        self.count_picking_late_soon = count.get(self.id, 0)

    count_picking_late_soon = fields.Integer(
        compute='_get_picking_count_late_soon')
