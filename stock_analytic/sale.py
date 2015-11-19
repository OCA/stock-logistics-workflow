# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models
from openerp.osv import fields


class sale_order(models.Model):
    _inherit = 'sale.order'

    def _prepare_order_line_procurement(self, cr, uid, order,
                                        line, group_id=False,
                                        context=None):
        res = super(
            sale_order, self)._prepare_order_line_procurement(
                cr, uid, order, line, group_id=group_id, context=context)
        if order.project_id:
            res['account_analytic_id'] = order.project_id.id
        return res


class procurement_order(models.Model):
    _inherit = "procurement.order"

    _columns = {
        'account_analytic_id': fields.many2one(
            'account.analytic.account', 'Analytic account'),
    }

    def _run_move_create(self, cr, uid, procurement, context=None):
        res = super(
            procurement_order, self)._run_move_create(
                cr, uid, procurement,  context=context)
        if procurement.account_analytic_id:
            res['account_analytic_id'] = procurement.account_analytic_id.id
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
