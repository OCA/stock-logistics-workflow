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
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FMT


class StockLocation(orm.Model):
    _inherit = "stock.location"

    def _product_get_multi_location_for_period(self, cr, uid, ids, period,
                                               product_ids=False, context=None,
                                               states=None,
                                               what=('in', 'out')):
        if context is None:
            context = {}
        if states is None:
            states = ['done']
        # Compute date from context and period
        # wich determine reference date for out stock computing
        if context.get('ref_date', False):
            date_ref = context['ref_date']
            past_date_ref = (datetime.strptime(context['ref_date'],
                                               DATE_FMT) +
                             relativedelta(months=-int(period),
                                           day=1,
                                           days=-1)).strftime(DATE_FMT)
        # if no date take today
        else:
            date_ref = datetime.now()
            past_date_ref = (datetime.now() +
                             relativedelta(months=-int(period),
                                           day=1,
                                           days=-1)).strftime(DATE_FMT)
        # Construct sql clause
        sql_clause = "and date_expected between '%s' and '%s' " \
            % (past_date_ref, date_ref)
        product_obj = self.pool.get('product.product')
        states_str = ','.join(map(lambda s: "'%s'" % s, states))
        if not product_ids:
            product_ids = product_obj.search(cr, uid, [])
        res = {}
        for id in product_ids:
            res[id] = 0.0
        if not ids:
            return res

        product2uom = {}
        for product in product_obj.browse(cr, uid, product_ids,
                                          context=context):
            product2uom[product.id] = product.uom_id.id

        prod_ids_str = ','.join(map(str, product_ids))
        location_ids_str = ','.join(map(str, ids))
        results = []
        results2 = []
        if 'in' in what:
            # all moves from a location out of the set to a location in the set
            cr.execute("""select sum(product_qty), product_id, product_uom
                          from stock_move
                          where location_id not in (
                       """ + location_ids_str +
                       ") and location_dest_id in (" +
                       location_ids_str +
                       ") and product_id in (" +
                       prod_ids_str + ") and state in (" +
                       states_str + ")" +
                       sql_clause +
                       "group by product_id,product_uom")
            results = cr.fetchall()
        if 'out' in what:
            # all moves from a location in the set to a location out of the set
            cr.execute("""select sum(product_qty), product_id, product_uom
                          from stock_move
                          where location_id in (
                       """ + location_ids_str +
                       ") and location_dest_id not in (" +
                       location_ids_str + ") and product_id  in (" +
                       prod_ids_str + ") and state in (" +
                       states_str + ") " +
                       sql_clause +
                       "group by product_id,product_uom")
            results2 = cr.fetchall()
        uom_obj = self.pool.get('product.uom')
        for amount, prod_id, prod_uom in results:
            amount = uom_obj._compute_qty(cr, uid, prod_uom, amount,
                                          context.get('uom', False) or
                                          product2uom[prod_id])
            res[prod_id] += amount
        for amount, prod_id, prod_uom in results2:
            amount = uom_obj._compute_qty(cr, uid, prod_uom, amount,
                                          context.get('uom', False) or
                                          product2uom[prod_id])
            res[prod_id] -= amount
        return res


class ProductProduct(orm.Model):

    _inherit = "product.product"

    def _get_product_obsolescence_func(states, what, period):
        def _product_obs(self, cr, uid, ids, name, arg, context=None):
            if context is None:
                context = {}
            loc_obj = self.pool.get('stock.location')

            if context.get('shop', False):
                cr.execute("""select warehouse_id
                              from sale_shop
                              where id=%s""",
                           (context['shop'],))
                res2 = cr.fetchone()
                if res2:
                    context['warehouse'] = res2[0]

            if context.get('warehouse', False):
                cr.execute("""select lot_stock_id
                              from stock_warehouse
                              where id=%s""",
                           (context['warehouse'],))
                res2 = cr.fetchone()
                if res2:
                    context['location'] = res2[0]

            if context.get('location', False):
                location_ids = [context['location']]
            else:
                # get the company location id
                mod_obj = self.pool.get('ir.model.data')
                result = mod_obj._get_id(cr, uid, 'stock',
                                         'stock_location_company')
                location_ids = [mod_obj.read(cr, uid,
                                             [result],
                                             ['res_id'])[0]['res_id']]

            # build the list of ids of children of the location given by id
            location_ids = loc_obj.search(cr, uid,
                                          [('location_id',
                                            'child_of',
                                            location_ids)],
                                          context=context)
            res = loc_obj._product_get_multi_location_for_period(
                cr, uid, location_ids, int(period), ids, context, states, what
            )
            for id in ids:
                res.setdefault(id, 0.0)
            return res

        return _product_obs

    # Considering all state for obsolescence
    # May be only done...
    _product_out_qty_till_12m = _get_product_obsolescence_func(
        ('confirmed', 'waiting', 'assigned', 'done'), ('out',), 12
    )
    _product_out_qty_till_24m = _get_product_obsolescence_func(
        ('confirmed', 'waiting', 'assigned', 'done'), ('out',), 24
    )

    _columns = {
        'outgoing_qty_till_12m':
        fields.function(_product_out_qty_till_12m,
                        method=True, type='float',
                        string='Outgoing last 12 month'),
        'outgoing_qty_till_24m':
        fields.function(_product_out_qty_till_24m,
                        method=True, type='float',
                        string='Outgoing last 24 month'),

        'depreciation': fields.selection([('no', 'No'),
                                          ('half', 'Half'),
                                          ('full', 'Full')],
                                         'Depreciation'),
    }

    _defaults = {
        'depreciation': 'no',
    }
