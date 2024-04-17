# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import ast

from odoo import _, api, fields, models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    weighing_operations = fields.Boolean(related="picking_type_id.weighing_operations")
    has_weighing_operations = fields.Boolean(compute="_compute_has_weighing_operations")

    @api.depends("picking_ids")
    def _compute_has_weighing_operations(self):
        for batch in self:
            batch.has_weighing_operations = batch.picking_ids.filtered(
                "has_weighing_operations"
            )

    def action_weighing_operations(self):
        """Weight operations for this picking"""
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_weighing.weighing_operation_action"
        )
        weighings = self.move_ids.filtered("has_weight")
        action["name"] = _("Weighing operations for %(name)s", name=self.name)
        action["domain"] = [("id", "in", weighings.ids)]
        action["context"] = dict(
            self.env.context,
            **ast.literal_eval(action["context"]),
            group_by=["picking_id"]
        )
        return action
