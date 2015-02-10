# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014-2015 Camptocamp SA
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

from openerp import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_order_line_procurement(self, cr, uid, order, line,
                                        group_id=False, context=None):
        _super = super(SaleOrder, self)
        vals = _super._prepare_order_line_procurement(cr, uid, order, line,
                                                      group_id=group_id,
                                                      context=context)
        if order.section_id.route_id and not vals.get('route_ids'):
            route = order.section_id.route_id
            routes = [(4, route.id)]
            vals['route_ids'] = routes
        return vals
