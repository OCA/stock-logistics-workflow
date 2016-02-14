# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-15 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import fields, osv


class StockConfigSettings(osv.TransientModel):
    _inherit = 'stock.config.settings'

    _columns = {
        'group_use_product_description_per_stock_move': fields.boolean(
            "Allow using only the product description on the stock moves",
            implied_group="stock_move_description."
            "group_use_product_description_per_stock_move",
            help="Allows you to use only product description on the "
            "stock moves."
        ),
    }
