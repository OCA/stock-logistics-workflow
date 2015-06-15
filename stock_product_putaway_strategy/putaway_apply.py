# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Bubbles-iT (<http://www.bubbles-it.be>)
#    Copyright (C) 2004 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from openerp.osv import fields, osv

class product_putaway_strategy(osv.Model): 
    _inherit = 'product.putaway'
 
    def putaway_apply(self, cr, uid, putaway_strat, product, context=None):
        if putaway_strat.method == 'fixed':
            #Check in Products first
            for strat in putaway_strat.fixed_location_by_product_ids:
                if product.id == strat.product_id.id:
                    return strat.fixed_location_id.id

            #Check in Categories
            for strat in putaway_strat.fixed_location_ids:
                categ = product.categ_id
                while categ:
                    if strat.category_id.id == categ.id:
                        return strat.fixed_location_id.id
                    categ = categ.parent_id

    _columns = { 
        'fixed_location_by_product_ids': fields.one2many('stock.fixed.putaway.byprod.strat', 'putaway_id', 'Fixed Locations Per Product Category',
             help='When the method is fixed, this location will be used to store the products', copy=True),
    }
 
class fixed_putaway_by_prod_strat(osv.Model):
    _name = 'stock.fixed.putaway.byprod.strat'
    _order = 'sequence'
    _columns = {
        'putaway_id': fields.many2one('product.putaway', 'Put Away Method', required=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'fixed_location_id': fields.many2one('stock.location', 'Location', required=True),
        'sequence': fields.integer('Priority', help="Give to the more specialized category, a higher priority to have them in top of the list."),
    }


