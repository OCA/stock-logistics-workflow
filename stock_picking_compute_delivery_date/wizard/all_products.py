# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Leonardo Pistone
#    Copyright 2014 Camptocamp SA
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

from openerp.osv import orm


class ComputeAllDeliveryDatesWizard(orm.TransientModel):

    _name = 'compute.all.delivery.dates.wizard'

    def do_compute(self, cr, uid, ids, context=None):
        """Delegate the picking to compute delivery dates for all products.

        If use_new_cursor is in the context, pass it as a parameter.

        """
        if context is None:
            context = {}
        pick_obj = self.pool['stock.picking']

        if 'use_new_cursor' in context:
            pick_obj.compute_all_delivery_dates(
                cr, uid, use_new_cursor=context['use_new_cursor'],
                context=context)
        else:
            pick_obj.compute_all_delivery_dates(cr, uid, context=context)

        return True
