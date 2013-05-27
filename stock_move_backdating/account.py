# -*- coding: utf-8 -*-
##############################################################################
#
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

from openerp.osv import fields, orm

class account_move(orm.Model):
    _inherit = "account.move"
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        period_obj = self.pool.get('account.period')
        if context.get('move_date'):
            period_ids = period_obj.find(cr, uid, dt=context['move_date'], context=context)
            if period_ids:
                vals['period_id'] = period_ids[0]
                vals['date'] = context['move_date']
        res = super(account_move,self).create(cr, uid, vals, context=context)
