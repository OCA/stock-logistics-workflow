# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) Camptocamp SA
# Author: Arnaud Wüst
#
#
#    This file is part of the c2c_planning_management module
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
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
                                         ['res_id'])[0]['res_id']
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
        tree_view_id = mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']

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
