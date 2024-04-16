# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import ast

from odoo import _, api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    weighing_operations = fields.Boolean(related="picking_type_id.weighing_operations")
    has_weighing_operations = fields.Boolean(compute="_compute_has_weighing_operations")

    @api.depends("move_lines")
    def _compute_has_weighing_operations(self):
        for picking in self:
            picking.has_weighing_operations = picking.move_lines.filtered("has_weight")

    def action_weighing_operations(self):
        """Weighing operations for this picking"""
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_weighing.weighing_operation_action"
        )
        weight_moves = self.move_lines.filtered("has_weight")
        action["name"] = _("Weighing operations for %(name)s", name=self.name)
        action["domain"] = [("id", "in", weight_moves.ids)]
        action["context"] = dict(
            self.env.context,
            **ast.literal_eval(action["context"]),
            group_by=["picking_id"]
        )
        return action
