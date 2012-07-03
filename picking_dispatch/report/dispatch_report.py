# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
#   @author Nicolas Bessi, Joel Grand-Guillaume
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
## -*- coding: utf-8 -*-

import operator
from report import report_sxw
import pooler

class NullMove(object):
    """helper class to generate empty lines in the delivery report"""
    def __init__(self):
        self.product_id = NullObj()
        self.dispatch_id = NullObj()
        self.product_qty = ''

class NullObj(object):
    """the null obj has any attribute you want with an empty string as the value"""
    def __getattr__(self, attr):
        return ''


class DispatchAgregation(object):

    def __init__(self, src_stock, dest_stock, move_ids, picker):
        self.src_stock = src_stock
        self.dest_stock = dest_stock
        self.move_ids = move_ids
        self.picker_id = picker

    def exists(self):
        return False

    def __hash__(self):
        return hash((self.src_stock.id, self.dest_stock.id))

    def __eq__(self, other):
        return (self.src_stock.id, self.dest_stock.id) == (other.src_stock.id, other.dest_stock.id)

    def moves_by_product(self):
        """iterate over moves sorted by product default_code"""
        return sorted(self.move_ids, key=operator.attrgetter('product_id.default_code'))

    def moves_by_picking(self):
        """iterate over moves sorted by picking name

        a NullMove is inserted for each new picking so that
        the report displays an empty line
        """
        name = None
        for move in sorted(self.move_ids, key=operator.attrgetter('picking_id.name')):
            if name is None:
                name = move.picking_id.name
            else:
                if move.picking_id.origin != name:
                    yield NullMove()
                    name = move.picking_id.name
            yield move

    def product_quantity(self):
        """iterate over the different products concerned by the moves
        with their total quantity, sorted by product default_code"""
        products = {}
        product_qty = {}
        carrier = {}
        print "DEBUG_-------------------"
        print self.move_ids
        for move in self.move_ids:
            p_code = move.product_id.default_code
            products[p_code] = move.product_id
            carrier[p_code] = move.picking_id.carrier_id and move.picking_id.carrier_id.partner_id.name or ''
            if p_code not in product_qty:
                product_qty[p_code] = move.product_qty
            else:
                product_qty[p_code] += move.product_qty
        for p_code in sorted(products):
            yield products[p_code], product_qty[p_code], carrier[p_code]

class PrintDispatch(report_sxw.rml_parse):

    def __init__(self, cursor, uid, name, context):
        super(PrintDispatch, self).__init__(cursor, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr
        self.numeration_type = False
        self.localcontext.update({})

    def _get_form_param(self, param, data, default=False):
        return data.get('form', {}).get(param, default) or default

    def set_context(self, objects, data, ids, report_type=None):
        #!! data form is manually set in wizard
        agreg = {}
        picker_dct = {}
        for dispatch in objects:
            for move in dispatch.move_ids:
                if move.state == 'assigned':
                    key = (move.location_id, move.location_dest_id)
                    agreg.setdefault(key, []).append(move)
                    picker_dct[key] = dispatch.picker_id
        objects = []
        for agr in agreg:
            print agr
            objects.append(DispatchAgregation(agr[0], agr[1], agreg[agr], picker_dct.get(agr,False)))
        return super(PrintDispatch, self).set_context(objects, data, ids, report_type=report_type)

report_sxw.report_sxw('report.webkit.dispatch_order',
                      'picking.dispatch',
                      'addons/picking_dispatch/report/dispatch.html.mako',
                      parser=PrintDispatch)
