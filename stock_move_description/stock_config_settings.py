# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018-19
#    (dvit.me>)
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

from odoo import fields, models,api

class StockConfigSettings(models.TransientModel):
    _inherit = 'stock.config.settings'


    group_use_product_description_per_stock_move = fields.Boolean(
        "Allow using only the product description on the stock moves",
        help="Allows you to use only product description on the "
        "stock moves."
        )


    @api.multi
    def set_group_product_desc_values(self):
        return self.env['ir.values'].sudo().set_default('stock.config.settings',
                                                        'group_use_product_description_per_stock_move',
                                                        self.group_use_product_description_per_stock_move)
