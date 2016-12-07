# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Chafique Delli
#    Copyright 2014 Akretion SA
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

from openerp.osv import orm, fields


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    _columns = {
        'line_parent_id': fields.many2one('sale.order.line', 'Parent Line'),
        'line_child_ids': fields.one2many('sale.order.line', 'line_parent_id',
                                          'Children Line'),
        }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        order_line = self.browse(cr, uid, id, context=context)
        if not order_line.line_parent_id:
            default = {
                'line_child_ids': False,
            }
        data = super(SaleOrderLine, self).copy_data(
            cr, uid, id, default=default, context=context)
        for child_line in order_line.line_child_ids:
            default = {
                'line_parent_id': id,
            }
            super(SaleOrderLine, self).copy_data(
                cr, uid, child_line.id, default=default, context=context)
        return data
