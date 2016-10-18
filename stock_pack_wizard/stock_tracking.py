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


class StockTracking(orm.Model):
    _inherit = 'stock.tracking'

    def _get_net_weight(
            self, cr, uid, ids, field_name, arg=None, context=None):
        '''Get total net weight in the pack.

        Sum net weight of all the stock moves in the pack

        @return: the total net weight.'''
        res = {}
        for pack in self.browse(cr, uid, ids, context=context):
            res[pack.id] = sum(
                [m.product_id.weight_net * m.product_qty
                    for m in pack.move_ids])
        return res

    _columns = {
        'ul_id': fields.many2one('product.ul', 'Pack Template'),
        'pack_h': fields.related(
            'ul_id', 'high', string='H (cm)',
            type='float',
            digits_compute=dp.get_precision('Pack Height'),
            readonly=True),
        'pack_w': fields.related(
            'ul_id', 'width', string='W (cm)',
            type='float',
            digits_compute=dp.get_precision('Pack Height'),
            readonly=True),
        'pack_l': fields.related(
            'ul_id', 'long', string='L (cm)',
            type='float',
            digits_compute=dp.get_precision('Pack Height'), readonly=True),
        'pack_cbm': fields.related(
            'ul_id', 'cbm', string='CBM', type='float',
            digits_compute=dp.get_precision('Pack Height'), readonly=True),
        'pack_address': fields.char('Address', size=128),
        'pack_note': fields.char('Note', size=128),

        'gross_weight': fields.float(
            'GW (Kg)',
            digits_compute=dp.get_precision('Pack Weight')),
        'net_weight': fields.function(
            _get_net_weight, arg=None,
            type='float', string='NW (Kg)',
            digits_compute=dp.get_precision('Pack Weight')),
    }


class StockMove(orm.Model):
    _inherit = 'stock.move'

    # TODO how to order records only for one specific list view?
    _order = 'date_expected desc, tracking_id asc, id'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
