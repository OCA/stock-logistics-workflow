# -*- coding: utf-8 -*-
#    Author: Leonardo Pistone
#    Copyright 2014, 2015 Camptocamp SA
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

from openerp.osv import orm


class ComputeDeliveryDateByProductWizard(orm.TransientModel):

    _name = 'compute.delivery.date.by.product.wizard'

    def do_compute(self, cr, uid, ids, context=None):
        pick_obj = self.pool['stock.picking']
        product_obj = self.pool['product.product']

        product_ids = context['active_ids']
        for product in product_obj.browse(cr, uid, product_ids,
                                          context=context):
            pick_obj.compute_delivery_dates(cr, uid, product, context=context)

        return True
