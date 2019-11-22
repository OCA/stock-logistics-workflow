# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import collections
import time

from openerp import pooler, api
from openerp.report import report_sxw

from . batch_aggregation import BatchAggregation


class PrintBatch(report_sxw.rml_parse):

    _aggregation_class = BatchAggregation

    @api.v7 # noqa
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
            pack_operations = collections.OrderedDict()
            for op in self.get_sorted_batch_pickings(batch.pack_operation_ids):
                id1, id2 = op.location_id.id, op.location_dest_id.id
                key_dict = dict(
                    location_obj.name_get(
                        self.cursor, self.uid, [id1, id2]
                    )
                )

                key = key_dict[id1], key_dict[id2]
                pack_operations.setdefault(key, []).append(op)
            new_objects.append(self._aggregation_class(batch, pack_operations))
        return super(PrintBatch, self).set_context(new_objects, data, ids,
                                                   report_type=report_type)

    def get_sorted_batch_pickings(self, pickings):
        """By default will be used order from model
        this place to customize sorting if needed"""
        return pickings
