# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import clean_context


class StockMoveWeightWizard(models.TransientModel):
    _name = "weighing.wizard"
    _description = "Record weights over detailed operations"
    _transient_max_hours = 0.1

    wizard_state = fields.Selection(
        selection=[
            ("weight", "Weight"),
            ("new_move_line", "Add Operation"),
        ],
        default="weight",
    )
    move_id = fields.Many2one(comodel_name="stock.move")
    product_id = fields.Many2one(
        comodel_name="product.product", related="move_id.product_id", store=True
    )
    available_lot_ids = fields.Many2many(
        comodel_name="stock.production.lot", compute="_compute_available_lot_ids"
    )
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot", domain="[('id', 'in', available_lot_ids)]"
    )
    product_tracking = fields.Selection(related="product_id.tracking")
    selected_move_line_id = fields.Many2one(comodel_name="stock.move.line")
    move_line_ids = fields.Many2many(comodel_name="stock.move.line")
    weight = fields.Float(digits="Product Unit of Measure")
    print_label = fields.Boolean(help="Print label after the weight record")
    label_report_id = fields.Many2one(comodel_name="ir.actions.report")

    @api.depends("product_id")
    def _compute_available_lot_ids(self):
        self.available_lot_ids = False
        for wiz in self.filtered(lambda x: x.product_id.tracking != "none"):
            wiz.available_lot_ids = self.env["stock.production.lot"].search(
                [("product_id", "=", wiz.product_id.id)],
                order="create_date desc",
                limit=5,
            )

    def _lot_creation_constraints(self):
        """To be hooked by stock_picking_auto_create_lot or others"""
        return [self.product_tracking != "none", not self.lot_id]

    def _check_lot_creation(self):
        """Avoid adding a detailed operation when no lot is set and it is required.
        This method can be a hook to allow using stock_picking_auto_create_lot to
        create the lots on the fly"""
        self.ensure_one()
        if all(self._lot_creation_constraints()):
            raise UserError(_("You need to supply a Lot/Serial Number"))

    def _post_add_detailed_operation(self):
        """To be hooked if necessary"""

    def add_operation_and_record(self):
        """New detailed operation from the kanban card"""
        vals = self.move_id._prepare_move_line_vals(quantity=self.weight)
        if self.lot_id:
            vals["lot_id"] = self.lot_id.id
        self._check_lot_creation()
        self.selected_move_line_id = (
            self.env["stock.move.line"]
            .with_context(**clean_context(self.env.context))
            .create(vals)
        )
        self._post_add_detailed_operation()
        return self.record_weight()

    def record_weight(self):
        """Register the operation weight"""
        selected_line = self.selected_move_line_id
        if self.weight:
            selected_line.qty_done = self.weight
            selected_line.recorded_weight = self.weight
            selected_line.has_recorded_weight = True
            selected_line.weighing_user_id = self.env.user
            selected_line.weighing_date = fields.Datetime.now()
        # Reset value
        else:
            selected_line.qty_done = 0
            selected_line.recorded_weight = 0
            selected_line.has_recorded_weight = False
            selected_line.weighing_user_id = False
            selected_line.weighing_date = False
        # Unlock the operation
        selected_line.move_id.action_unlock_weigh_operation()
        if self.print_label:
            action = selected_line.action_print_weight_record_label()
            action["close_on_report_download"] = True
            return action

    def action_close(self):
        """Close but unlock the operation"""
        (
            self.move_id or self.selected_move_line_id.move_id
        ).action_unlock_weigh_operation()

    def unlink(self):
        """Ensure that the wizard cleanup releases the weighing operations"""
        (self.move_id | self.selected_move_line_id.move_id).weighing_user_id = False
        return super().unlink()
