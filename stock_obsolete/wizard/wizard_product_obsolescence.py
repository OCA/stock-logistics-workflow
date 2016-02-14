# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joël Grand-Guillaume, Matthieu Dietrich
#    Copyright 2008-2015 Camptocamp SA
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

from osv import fields, orm


class wizard_product_obsolescence(orm.TransientModel):
    _name = "wizard.product.obsolescence"

    def _location_default_get(self, cr, uid, context):
        # get the company location id
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj._get_id(cr, uid, 'stock', 'stock_location_company')
        stock_location_id = mod_obj.read(cr, uid,
                                         [result],
                                         ['res_id'],
                                         context=context)[0]['res_id']
        return stock_location_id

    _columns = {
        'location': fields.many2one('stock.location',
                                    'From location',
                                    required=True),
        'to_date': fields.date('Obsolescence to date',
                               required=True),
    }

    _defaults = {
        'location': lambda self, cr, uid, context:
        self._location_default_get(cr, uid, context=context),
        'to_date': lambda *a: fields.datetime.now(),
    }

    def button_open(self, cr, uid, ids, context=None):
        # get view
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj._get_id(cr, uid, 'stock_obsolete',
                                 'product_product_obsolet_tree_view')
        tree_view_id = mod_obj.read(cr, uid,
                                    [result], ['res_id'],
                                    context=context)[0]['res_id']

        # take only stockable product type
        wizard = self.browse(cr, uid, ids, context=context)[0]

        value = {
            'domain': "[('type','=','product')]",
            'name': 'Product obsolescence',
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'product.product',
            'view_id': [tree_view_id],
            'type': 'ir.actions.act_window',
            'limit': 4000,
            'context': "{'ref_date':'%s','location':%s}"
            % (wizard['to_date'], wizard['location'].id)
        }
        return value

    def button_report(self, cr, uid, ids, context=None):
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['location', 'to_date'])[0]
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'product.obsolete',
            'datas': data,
        }
