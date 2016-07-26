# -*- coding: utf-8 -*-
# © 2012-2014 Nicolas Bessi, Joel Grand-Guillaume, Alexandre Fayolle
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import time
from os.path import commonprefix
from openerp.report import report_sxw
from openerp import pooler, models

_logger = logging.getLogger(__name__)


class BatchAggregation(object):
    """ Group operations from a single batch by source and dest locations
    """

    def __init__(self, batch_id, operations_by_loc):
        self.batch_id = batch_id
        self.operations_by_loc = operations_by_loc

    def exists(self):
        return False

    @property
    def picker_id(self):
        return self.batch_id.picker_id

    @property
    def batch_name(self):
        return self.batch_id.name

    @property
    def batch_notes(self):
        return self.batch_id.notes or u''

    def __hash__(self):
        return hash(self.batch_id.id)

    def __eq__(self, other):
        return self.batch_id.id == other.batch_id.id

    def iter_locations(self):
        """ Iterate over operations grouped by (loc_source, loc_dest)
        and return informations to display in report for these locs.

        Informations are like:
        (
            (loc_source_name, loc_dest_name),
            (
                (product1, product1_qty, product1_carrier)
                (product2, product2_qty, product2_carrier)
                [...]
            )
        )
        """
        for locations in self.operations_by_loc:
            offset = commonprefix(locations).rfind('/') + 1
            display_locations = tuple(
                loc[offset:].strip() for loc in locations
            )
            yield display_locations, self._product_quantity(locations)

    def _product_quantity(self, locations):
        """ Iterate over the different products concerned by the operations for
        the specified locations with their total quantity, sorted by product
        default_code

        locations: a tuple (source_location, dest_location)
        """
        products = {}
        product_qty = {}
        carrier = {}
        operations = self.operations_by_loc[locations]
        for operation in operations:
            p_code = operation.product_id.default_code
            products[p_code] = operation.product_id
            carrier[p_code] = (
                operation.picking_id.carrier_id and
                operation.picking_id.carrier_id.partner_id.name or ''
            )
            if p_code not in product_qty:
                product_qty[p_code] = operation.product_qty
            else:
                product_qty[p_code] += operation.product_qty
        for p_code in sorted(products):
            yield products[p_code], product_qty[p_code], carrier[p_code]


class PrintBatch(report_sxw.rml_parse):

    def __init__(self, cursor, uid, name, context):
        super(PrintBatch, self).__init__(cursor, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr
        self.uid = uid
        self.numeration_type = False
        self.localcontext.update({
            'time': time,
            'get_location_datas': self._get_location_datas,
        })

    def _get_location_datas(self, aggr):
        for loc in aggr.iter_locations():
            yield loc

    def _get_form_param(self, param, data, default=False):
        return data.get('form', {}).get(param, default) or default

    def set_context(self, objects, data, ids, report_type=None):
        new_objects = []
        location_obj = self.pool.get('stock.location')
        for batch in objects:
            pack_operations = {}
            for op in batch.pack_operation_ids:
                id1, id2 = op.location_id.id, op.location_dest_id.id
                key_dict = dict(
                    location_obj.name_get(
                        self.cursor, self.uid, [id1, id2]
                    )
                )

                key = key_dict[id1], key_dict[id2]
                pack_operations.setdefault(key, []).append(op)
            new_objects.append(BatchAggregation(batch, pack_operations))
        return super(PrintBatch, self).set_context(new_objects, data, ids,
                                                   report_type=report_type)


class ReportPrintBatchPicking(models.AbstractModel):
    _name = 'report.stock_batch_picking.report_batch_picking'
    _inherit = 'report.abstract_report'
    _template = 'stock_batch_picking.report_batch_picking'
    _wrapped_report_class = PrintBatch
