# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import ast

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move", "weighing.mixin"]

    recorded_weight = fields.Float(
        compute="_compute_recorded_weight", digits="Product Unit of Measure"
    )
    move_lines_weighed = fields.Boolean(compute="_compute_recorded_weight")
    weighing_state = fields.Selection(
        selection=[
            ("weighed", "Weighed"),
            ("weighing", "Weighing"),
            ("to_weigh", "To weigh"),
        ],
        compute="_compute_weighing_state",
        store=True,
    )
    weighing_user_id = fields.Many2one(
        comodel_name="res.users",
        help="This user is weighing the record, so it's locked by him",
    )
    is_weighing_operation_locked = fields.Boolean(
        compute="_compute_is_weighing_operation_locked"
    )
    lot_names = fields.Char(compute="_compute_lot_names")
    origin_names = fields.Char(compute="_compute_origin_names")
    # HACK: To show the kanban of this move in its own form
    self_move_ids = fields.Many2many(
        comodel_name="stock.move", compute="_compute_self_move_ids"
    )

    def name_get(self):
        if not self.env.context.get("weight_operation_details"):
            return super().name_get()
        return [(move.id, _("%(name)s details", name=move.name)) for move in self]

    def _compute_self_move_ids(self):
        for move in self:
            move.self_move_ids = self

    @api.depends("move_line_ids.recorded_weight")
    def _compute_recorded_weight(self):
        for move in self:
            move.recorded_weight = sum(move.move_line_ids.mapped("recorded_weight"))
            move.move_lines_weighed = move.move_line_ids and all(
                move.move_line_ids.mapped("recorded_weight")
            )

    @api.depends("move_line_ids.recorded_weight", "state", "product_id")
    def _compute_weighing_state(self):
        """Only products with weight will trigger this state"""
        self.weighing_state = False
        for move in self.filtered("has_weight"):
            move_to_do = move.state not in {"draft", "cancel", "done"}
            if (
                move.move_lines_weighed
                # Force the operation weighing state if one of the detailed
                # operations overpasses the demand
                or float_compare(
                    move.quantity_done,
                    move.product_uom_qty,
                    precision_rounding=move.product_uom.rounding,
                )
                >= 0
            ) and any(move.move_line_ids.mapped("has_recorded_weight")):
                move.weighing_state = "weighed"
            elif move.recorded_weight and not move.move_lines_weighed and move_to_do:
                move.weighing_state = "weighing"
            elif (
                not move.recorded_weight
                and not move.move_lines_weighed
                and move_to_do
                and not move.quantity_done
            ):
                move.weighing_state = "to_weigh"

    @api.depends("move_line_ids.lot_id")
    def _compute_lot_names(self):
        """To use in the kanban and show the list of lots for this move"""
        self.lot_names = False
        for move in self:
            move.lot_names = ",".join(move.move_line_ids.lot_id.mapped("name"))

    @api.depends("move_line_ids.location_id")
    def _compute_origin_names(self):
        """To use in the kanban and show the origin locations on this move reservation"""
        self.origin_names = False
        for move in self:
            move.origin_names = ",".join(move.move_line_ids.location_id.mapped("name"))

    @api.depends("weighing_user_id", "state")
    def _compute_is_weighing_operation_locked(self):
        """Out own operations won't show up as locked"""
        self.is_weighing_operation_locked = False
        self.filtered(
            lambda x: x.state not in {"cancel", "draft", "done"}
            and x.weighing_user_id
            and x.weighing_user_id != self.env.user
        ).is_weighing_operation_locked = True

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """We need to sort by move sub-fields. Don't force if we have a given order"""
        moves = super().search(args, offset, limit, order, count)
        if not count and self.env.context.get("outgoing_weighing_order") and not order:
            moves = moves.sorted(
                lambda x: (
                    x.location_id.name or "",
                    x.product_id.default_code or "",
                    x.product_id.name or "",
                )
            )
        return moves

    def action_lock_weighing_operation(self):
        """Avoid other that other user to modify the weight operation"""
        self.ensure_one()
        if self.weighing_user_id and self.weighing_user_id != self.env.user:
            raise UserError(
                _(
                    "The user %(user)s is already weighing this operation",
                    user=self.weighing_user_id.name,
                )
            )
        self.weighing_user_id = self.env.user

    def action_unlock_weigh_operation(self):
        """Unlock the weigh operation"""
        self.ensure_one()
        self.weighing_user_id = False

    def action_weighing(self):
        """Open the wizard to record weights"""
        self.action_lock_weighing_operation()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_weighing.weighing_wizard_action"
        )
        action["name"] = fields.first(self.move_line_ids)._get_action_weighing_name()
        action["context"] = dict(
            self.env.context,
            default_selected_move_line_id=(fields.first(self.move_line_ids).id),
            default_weight=self.recorded_weight or self.quantity_done,
            default_move_line_ids=self.move_line_ids.ids,
            default_print_label=self.picking_type_id.print_weighing_label,
        )
        return action

    def action_add_move_line(self):
        """Open the weight wizard to add a new operation weight"""
        action = self.action_weighing()
        action["context"].update(
            default_wizard_state="new_move_line",
            default_move_id=self.id,
            default_weight=0,
        )
        del action["context"]["default_selected_move_line_id"]
        action["name"] = _(
            "New operation for %(product)s (%(operation)s) "
            "%(remain).2f %(uom)s remaining",
            product=self.product_id.name,
            operation=self.reference,
            remain=max((self.product_uom_qty - self.quantity_done), 0),
            uom=self.product_uom.name,
        )
        return action

    def action_weight_detailed_operations(self):
        """Weight detailed operations for this picking"""
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_weighing.weighing_operation_action"
        )
        action["name"] = _("Detailed operations for %(name)s", name=self.name)
        action["domain"] = [("id", "=", self.id)]
        action["view_mode"] = "form"
        action["res_id"] = self.id
        action["views"] = [
            (view, mode) for view, mode in action["views"] if mode == "form"
        ]
        action["context"] = dict(
            self.env.context,
            **ast.literal_eval(action["context"]),
            weight_operation_details=True
        )
        return action

    def action_print_weight_record_label(self):
        """Get operations labels"""
        return self.move_line_ids.action_print_weight_record_label()

    def action_reset_weights(self):
        """Restore stock move lines weights"""
        self.move_line_ids.action_reset_weights()

    def action_force_weighed(self):
        self.weighing_state = "weighed"

    @api.model
    def action_outgoing_weighing_operations(self):
        """Used in the start screen"""
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_weighing.weighing_operation_action"
        )
        action["domain"] = [
            ("has_weight", "=", True),
            ("location_id.usage", "in", ["internal", "transit"]),
            ("location_dest_id.usage", "not in", ["internal", "transit"]),
            ("picking_type_id.weighing_operations", "=", True),
        ]
        action["target"] = "main"
        action["name"] = _("Weight outgoing")
        return action

    @api.model
    def action_incoming_weighing_operations(self):
        """Used in the start screen"""
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_weighing.weighing_operation_action"
        )
        action["domain"] = [
            ("has_weight", "=", True),
            ("location_id.usage", "not in", ["internal", "transit"]),
            ("location_dest_id.usage", "in", ["internal", "transit"]),
            ("picking_type_id.weighing_operations", "=", True),
        ]
        action["target"] = "main"
        action["name"] = _("Weight incoming")
        return action
