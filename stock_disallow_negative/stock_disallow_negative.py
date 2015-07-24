# -*- encoding: utf-8 -*-
##############################################################################
#
#    Stock Disallow Negative module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    allow_negative_stock = fields.Boolean(
        string='Allow Negative Stock',
        help="Allow negative stock levels for the stockable products "
        "attached to this category. The options doesn't apply to products "
        "attached to sub-categories of this category.")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allow_negative_stock = fields.Boolean(
        string='Allow Negative Stock',
        help="If this option is not active on this product nor on its "
        "product category and that this product is a stockable product, "
        "then the validation of the related stock moves will be blocked if "
        "the stock level becomes negative with the stock move.")


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.one
    @api.constrains('product_id', 'qty')
    def check_negative_qty(self):
        if (
                self.qty < 0 and
                self.product_id.type == 'product' and
                not self.product_id.allow_negative_stock and
                not self.product_id.categ_id.allow_negative_stock):
            raise ValidationError(
                _("You cannot valide this stock operation because the stock "
                  "level of the product '%s' would become negative on the "
                  "stock location '%s' and negative stock is not allowed "
                  "for this product.")
                % (self.product_id.name, self.location_id.complete_name))
