# -*- coding: utf-8 -*-
# © 2012-2014 Nicolas Bessi, Joel Grand-Guillaume, Alexandre Fayolle
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import time
from os.path import commonprefix
from openerp.report import report_sxw
from openerp import pooler, models

_logger = logging.getLogger(__name__)


class NullMove(object):

    """helper class to generate empty lines in the delivery report"""

    def __init__(self):
        self.product_id = NullObj()
        self.dispatch_id = NullObj()
        self.product_qty = ''


class NullObj(object):

    """the null obj has any attribute you want with an empty string as the
    value"""

    def __getattr__(self, attr):
        return ''


class DispatchAgregation(object):

    """group moves from a single dispatch by source and dest locations"""

    def __init__(self, dispatch, moves_by_loc):
        self.dispatch_id = dispatch
        self.moves_by_loc = moves_by_loc

    @property
    def picker_id(self):
        return self.dispatch_id.picker_id

    @property
    def dispatch_name(self):
        return self.dispatch_id.name

    @property
    def dispatch_notes(self):
        return self.dispatch_id.notes or u''

    def exists(self):
        return False

    def __hash__(self):
        return hash(self.dispatch_id.id)

    def __eq__(self, other):
        return (self.dispatch_id.id == other.dispatch_id.id)

    def iter_locations(self):
        for locations in self.moves_by_loc:
            offset = commonprefix(locations).rfind('/') + 1
            display_locations = tuple(
                loc[offset:].strip() for loc in locations)
            yield display_locations, self._product_quantity(locations)

    def _product_quantity(self, locations):
        """iterate over the different products concerned by the moves for the
        specified locations with their total quantity, sorted by product
        default_code

        locations: a tuple (source_location, dest_location)
        """
        products = {}
        product_qty = {}
        carrier = {}
        moves = self.moves_by_loc[locations]
        _logger.debug('move ids %s', moves)
        for move in moves:
            p_code = move.product_id.default_code
            products[p_code] = move.product_id
            carrier[p_code] = (
                move.picking_id.carrier_id and
                move.picking_id.carrier_id.partner_id.name or ''
            )
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
        self.uid = uid
        self.numeration_type = False
        self.localcontext.update({
            'time': time,
            'has_variants': self._has_variants,
            'get_location_datas': self._get_location_datas,
        })

    def _has_variants(self, aggr):
        has_variants = False
        for locations, product_quantities in aggr.iter_locations():
            for product, qty, carrier in product_quantities:
                if product.product_variant_count > 1:
                    has_variants = True
                    break
            else:
                continue
            break
        return has_variants

    def _get_location_datas(self, aggr):
        for loc in aggr.iter_locations():
            yield loc

    def _get_form_param(self, param, data, default=False):
        return data.get('form', {}).get(param, default) or default

    def set_context(self, objects, data, ids, report_type=None):
        # !! data form is manually set in wizard
        new_objects = []
        location_obj = self.pool.get('stock.location')
        for dispatch in objects:
            moves_by_loc = {}
            for move in dispatch.move_ids:
                if move.state == 'assigned':
                    id1, id2 = move.location_id.id, move.location_dest_id.id
                    key_dict = dict(
                        location_obj.name_get(
                            self.cursor, self.uid, [id1, id2]
                        )
                    )

                    key = key_dict[id1], key_dict[id2]
                    moves_by_loc.setdefault(key, []).append(move)
            _logger.debug('agreg %s ', moves_by_loc)
            new_objects.append(DispatchAgregation(dispatch, moves_by_loc))
        return super(PrintDispatch, self).set_context(new_objects, data, ids,
                                                      report_type=report_type)


class ReportPrintDispatch(models.AbstractModel):
    _name = 'report.stock_picking_dispatch.report_picking_dispatch'
    _inherit = 'report.abstract_report'
    _template = 'stock_picking_dispatch.report_picking_dispatch'
    _wrapped_report_class = PrintDispatch
