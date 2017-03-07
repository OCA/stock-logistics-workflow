# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.report import report_sxw

from . batch_aggregation import BatchAggregation


class PrintBatch(report_sxw.rml_parse):

    def __init__(self, cursor, uid, name, context):
        super(PrintBatch, self).__init__(cursor, uid, name, context=context)
        self.numeration_type = False
        self.localcontext.update({
            'get_location_datas': self._get_location_datas,
        })

    def _get_location_datas(self, aggr):
        for loc in aggr.iter_locations():
            yield loc

    def _get_form_param(self, param, data, default=False):
        return data.get('form', {}).get(param, default) or default

    def set_context(self, objects, data, ids, report_type=None):
        new_objects = []
        location_obj = self.localcontext['user'].env['stock.location']
        for batch in objects:
            pack_operations = {}
            for op in batch.pack_operation_ids:
                id1, id2 = op.location_id.id, op.location_dest_id.id
                key_dict = dict(
                    location_obj.browse([id1, id2]).name_get()
                )

                key = key_dict[id1], key_dict[id2]
                pack_operations.setdefault(key, []).append(op)
            new_objects.append(BatchAggregation(batch, pack_operations))
        return super(PrintBatch, self).set_context(new_objects, data, ids,
                                                   report_type=report_type)
