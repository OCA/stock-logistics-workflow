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

import time
import re
from report import report_sxw
from openerp.tools.translate import _


class ProductObsolete(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ProductObsolete, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'comma_me': self.comma_me,
            'get_name_of': self.get_depreciation_name,
        })
        self.context = context

    def comma_me(self, amount):
        if type(amount) is float:
            amount = str('%.2f' % amount)
        else:
            amount = str(amount)
        orig = amount
        new = re.sub(r"^(-?\d+)(\d{3})", r"\g<1>'\g<2>", amount)
        if orig == new:
            return new
        else:
            return self.comma_me(new)

    def get_depreciation_name(self, value):
        if value == 'no':
            return _('No')
        elif value == 'half':
            return _('Half')
        elif value == 'full':
            return _('Full')
        else:
            return False

    def set_context(self, objects, data, ids, report_type=None):
        prod_obj = self.pool.get('product.product')
        if (data.get('ids', False) and
            data.get('model', False) == 'product.product'):
            ids = [data['ids']]
        else:
            ids = prod_obj.search(self.cr, self.uid,
                                  [('type', '=', 'product')],
                                  limit=4000)

        objects = prod_obj.browse(self.cr, self.uid, ids)

        def o_compare(x, y):
            if x.outgoing_qty_till_12m < y.outgoing_qty_till_12m:
                return 1
            elif x.outgoing_qty_till_12m == y.outgoing_qty_till_12m:
                return 0
            else:  # x<y
                return -1

        # sort object by depreciation 12 month
        objects.sort(o_compare)
        self.ids = [o.id for o in objects]
        self.localcontext['objects'] = objects

report_sxw.report_sxw('report.product.obsolete',
                      'product.product',
                      'addons/stock_obsolete/report/product_obsolete.rml',
                      parser=ProductObsolete, header=False)
