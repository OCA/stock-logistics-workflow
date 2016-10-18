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

import time
from openerp.report import report_sxw


class StockTracklingList(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(StockTracklingList, self).__init__(
            cr, uid, name, context=context)
        self.context = context
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
            'get_total_qty': self._get_total_qty,
            'get_measurement': self._get_measurement,
            'get_cbm': self._get_cbm,
            'get_description': self._get_description,
            'sum_total_qty': self._sum_total_qty,
            'sum_pack_qty': self._sum_pack_qty,
            'sum_pack_nw': self._sum_pack_nw,
            'sum_pack_gw': self._sum_pack_gw,
            'sum_pack_cbm': self._sum_pack_cbm,
        })

    def _get_description(self, product_id):
        product = self.pool.get('product.product').browse(self.cr, self.uid, product_id)
        default_code = product.default_code and '[' + product.default_code + ']' or ''
        hs_code = product.hs_code and ' HS Code:' + product.hs_code or ''
        customs_description = product.customs_description and ' \n\n\n' + product.customs_description or ''
        return ''.join([default_code, customs_description, hs_code])

    def _get_total_qty(self, tracking_id):
        tracking = self.pool.get('stock.tracking').browse(self.cr, self.uid, tracking_id)
        return sum([line.product_qty for line in tracking.move_ids])

    def _get_measurement(self, tracking_id):
        tracking = self.pool.get('stock.tracking').browse(self.cr, self.uid, tracking_id)
        return r'*'.join([str(tracking.pack_h), str(tracking.pack_w), str(tracking.pack_l)] )

    def _get_cbm(self, tracking_id):
        tracking = self.pool.get('stock.tracking').browse(self.cr, self.uid, tracking_id)
        cbm = tracking.pack_h * tracking.pack_w * tracking.pack_l
        return cbm and cbm / 1000000.0 or 0.0

    def _sum_total_qty(self):
        tracking_ids = self.context.get('active_ids', [])
        return sum([self._get_total_qty(id) for id in tracking_ids])

    def _sum_pack_qty(self):
        return len(self.context.get('active_ids', []))

    def _sum_pack_nw(self):
        tracking_ids = self.context.get('active_ids', [])
        packs_nw = self.pool.get('stock.tracking').read(self.cr, self.uid, tracking_ids, ['net_weight'])
        return sum([x['net_weight'] for x in packs_nw])

    def _sum_pack_gw(self):
        tracking_ids = self.context.get('active_ids', [])
        packs_nw = self.pool.get('stock.tracking').read(self.cr, self.uid, tracking_ids, ['gross_weight'])
        return sum([x['gross_weight'] for x in packs_nw])

    def _sum_pack_cbm(self):
        tracking_ids = self.context.get('active_ids', [])
        return sum([self._get_cbm(id) for id in tracking_ids])


report_sxw.report_sxw('report.webkit_stock_tracking', 'stock.tracking', 'extra_addons/mmx_pack/report/stock_trackling_list.mako', parser=StockTracklingList, header='pack_list',)
report_sxw.report_sxw('report.rml_stock_tracking', 'stock.tracking', 'extra_addons/mmx_pack/report/stock_trackling_list.rml',  parser=StockTracklingList,)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
