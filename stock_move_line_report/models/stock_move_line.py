# Copyright 2025 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    allowed_to_print_label = fields.Boolean(compute="_compute_allowed_to_print_label")

    def _compute_allowed_to_print_label(self):
        self.allowed_to_print_label = False
        self.filtered(
            "picking_type_id.move_line_label_report_id"
        ).allowed_to_print_label = True

    def action_print_operation_label(self):
        """Get detailed operations labels"""
        return self.picking_type_id.move_line_label_report_id.report_action(self)
