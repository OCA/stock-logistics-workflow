# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models
from odoo.tools import float_is_zero


_logger = logging.getLogger(__name__)


class ReportPrintBatchPicking(models.AbstractModel):
    _name = 'report.stock_picking_batch_extended.report_batch_picking'
    _description = 'Report for Batch Picking'

    @api.model
    def key_level_0(self, operation):
        return operation.location_id.id, operation.location_dest_id.id

    @api.model
    def key_level_1(self, operation):
        return operation.product_id.id

    @api.model
    def new_level_0(self, operation):
        level_0_name = '{} \u21E8 {}'.format(
            operation.location_id.name_get()[0][1],
            operation.location_dest_id.name_get()[0][1])
        return {
            'name': level_0_name,
            'location': operation.location_id,
            'location_dest': operation.location_dest_id,
            'l1_items': {},
        }

    @api.model
    def new_level_1(self, operation):
        return {
            'product': operation.product_id,
            'product_qty': not float_is_zero(operation.product_qty)
            or operation.qty_done,
            'operations': operation,
        }

    @api.model
    def update_level_1(self, group_dict, operation):
        group_dict['product_qty'] += (
            not float_is_zero(operation.product_qty) or operation.qty_done
        )
        group_dict['operations'] += operation

    @api.model
    def sort_level_0(self, rec_list):
        return sorted(rec_list, key=lambda rec: (
            rec['location'].posx, rec['location'].posy, rec['location'].posz,
            rec['location'].name))

    @api.model
    def sort_level_1(self, rec_list):
        return sorted(rec_list, key=lambda rec: (
            rec['product'].default_code or '', rec['product'].id))

    @api.model
    def _get_grouped_data(self, batch):
        grouped_data = {}
        for op in batch.move_line_ids:
            l0_key = self.key_level_0(op)
            if l0_key not in grouped_data:
                grouped_data[l0_key] = self.new_level_0(op)
            l1_key = self.key_level_1(op)
            if l1_key in grouped_data[l0_key]['l1_items']:
                self.update_level_1(
                    grouped_data[l0_key]['l1_items'][l1_key], op)
            else:
                grouped_data[l0_key]['l1_items'][l1_key] = self.new_level_1(op)
        for l0_key in grouped_data.keys():
            grouped_data[l0_key]['l1_items'] = self.sort_level_1(
                grouped_data[l0_key]['l1_items'].values())
        return self.sort_level_0(grouped_data.values())

    @api.model
    def _get_report_values(self, docids, data=None):
        model = 'stock.picking.batch'
        docs = self.env[model].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'get_grouped_data': self._get_grouped_data,
            'now': fields.Datetime.now,
        }
