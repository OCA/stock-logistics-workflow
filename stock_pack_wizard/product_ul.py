# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
#    Jon Chow <jon.chow@elico-corp.com>
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
import openerp.addons.decimal_precision as dp


class ProductUl(orm.Model):
    _inherit = 'product.ul'

    def _get_cbm(self, cr, uid, ids, fields, arg=None, context=None):
        res = {}
        for ul in self.browse(cr, uid, ids, context=context):
            cbm = ul.high * ul.width * ul.long
            cbm = cbm != 0 and cbm / 1000000
            res[ul.id] = cbm
        return res

    _columns = {
        # re-define this field to change the size.
        'name': fields.char(
            'name', size=32,
            select=True, required=True, translate=True),
        'high': fields.float(
            'H (cm)', digits_compute=dp.get_precision('Pack Height')),
        'width': fields.float(
            'W (cm)', digits_compute=dp.get_precision('Pack Height')),
        'long': fields.float(
            'L (cm)', digits_compute=dp.get_precision('Pack Height')),
        'cbm': fields.function(
            _get_cbm, arg=None, type='float',
            string='CBM',
            digits_compute=dp.get_precision('Pack Height')),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
