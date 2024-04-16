# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import ast

from odoo import _, api, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    weighing_operations = fields.Boolean(
        help="Weighed products are done from weighing operations"
    )
    print_weighing_label = fields.Boolean(
        help="Print the weight operation label automatically"
    )
    weighing_label_report_id = fields.Many2one(
        comodel_name="ir.actions.report",
        domain=[("model", "=", "stock.move.line")],
        help="Choose a custom label template for this operation type",
    )
    weight_move_ids = fields.Many2many(
        comodel_name="stock.move", compute="_compute_weight_move_ids"
    )
    to_do_weights = fields.Integer(compute="_compute_to_do_weights")

    def _compute_weight_move_ids(self):
        for picking_type in self:
            picking_type.weight_move_ids = self.env["stock.move"].search(
                [
                    ("picking_type_id", "=", picking_type.id),
                    ("state", "in", ("assigned", "confirmed", "waiting")),
                    ("has_weight", "=", True),
                ]
            )

    @api.depends("weight_move_ids")
    def _compute_to_do_weights(self):
        for picking_type in self:
            picking_type.to_do_weights = len(picking_type.weight_move_ids)

    def action_weighing_operations(self):
        """Weighing operations for this picking"""
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_weighing.weighing_operation_action"
        )
        action["name"] = _("%(name)s Weighing operations", name=self.name)
        action["domain"] = [("id", "in", self.weight_move_ids.ids)]
        action["context"] = dict(
            self.env.context,
            **ast.literal_eval(action["context"]),
            group_by=["picking_id"]
        )
        return action
