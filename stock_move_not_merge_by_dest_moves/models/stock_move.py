# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        """Do not merge moves that goes to different destination moves"""
        fields = super()._prepare_merge_moves_distinct_fields()
        fields.append("move_dest_ids")
        return fields

    @api.model
    def _prepare_merge_negative_moves_excluded_distinct_fields(self):
        """Merge negative moves that goes to same destination moves"""
        fields = super()._prepare_merge_negative_moves_excluded_distinct_fields()
        fields.append("move_dest_ids")
        return fields
