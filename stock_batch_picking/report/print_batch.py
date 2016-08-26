# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from openerp import pooler
from openerp.report import report_sxw

from batch_aggregation import BatchAggregation


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
