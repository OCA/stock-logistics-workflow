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

#from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.one
    @api.depends('sale_id', 'requested_date')
    def compute_requested_date(self):
        if self.sale_id.requested_date:
            requested_date = self.sale_id.requested_date
        else:
            delay = 0
            for line in self.sale_id.order_line:
                if line.delay > delay:
                    delay = line.delay
            date_confirm_dt = fields.Date.from_string(
                self.sale_id.date_confirm)
            requested_date_dt = date_confirm_dt + relativedelta(
                days=delay or 0.0)
            requested_date = fields.Date.to_string(requested_date_dt)
        self.requested_date = requested_date

    requested_date = fields.Date(
        string='Requested Date',
        compute='compute_requested_date',
        readonly=True,
        help="The date requested for product availability to the customer."
             " If this date is set in the sale order then it will be used."
             " Otherwise we will use the order confirmation date,"
             " increased of the greatest delivery lead time on order lines.")


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    @api.multi
    @api.depends('name', 'code', 'warehouse_id')
    def _get_picking_count(self, field_names, arg):
        obj = self.pool.get('stock.picking')
        import pdb;pdb.set_trace()
        result = super(StockPickingType, self)._get_picking_count(
            field_names, arg)
        domains = {
            'count_picking_late_soon': [
                ('requested_date', '<', ),
                ('state', 'not in', ('cancel', 'done')),
                ('picking_type_id', 'in', self.ids)
            ]
        }
        for field in domains:
            data = obj.read_group(
                domains[field],
                ['picking_type_id'],
                ['picking_type_id']
            )
            count = dict(map(lambda x: (
                x['picking_type_id'] and x['picking_type_id'][0],
                x['picking_type_id_count']), data)
            )
            for tid in self.ids:
                result.setdefault(tid, {})[field] = count.get(tid, 0)
        return result

    count_picking_late_soon = fields.Integer(compute='_get_picking_count')
