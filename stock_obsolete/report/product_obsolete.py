#!/usr/bin/env python2.3
#
#  print_invoice_list.py
#  PEG
#
#  Created by Nicolas Bessi on 13.10.08.
#  Copyright (c) 2008 CamptoCamp. All rights reserved.
#

import time
from report import report_sxw
import re


class Product_obsolete(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Product_obsolete, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            # 'lines': self.lines,
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
        new = re.sub("^(-?\d+)(\d{3})", "\g<1>'\g<2>", amount)
        if orig == new:
            return new
        else:
            return self.comma_me(new)

    def get_depreciation_name(self, value):
        if value == 'no':
            return 'No'
        elif value == 'half':
            return 'Half'
        elif value == 'full':
            return 'Full'
        else:
            return False

    def set_context(self, objects, data, ids, report_type=None):
        prod_obj = self.pool.get('product.product')
        if data.get('ids', False) and \
           data.get('model', False) == 'product.product':
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
                      parser=Product_obsolete, header=False)
