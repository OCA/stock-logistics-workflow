# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models


class StockMoveLine(models.Model):
    _name = "stock.move.line"
    _inherit = ["stock.move.line", "weighing.mixin"]

    has_recorded_weight = fields.Boolean(help="The weight was set from the wizard")
    recorded_weight = fields.Float(digits="Product Unit of Measure")
    weighing_user_id = fields.Many2one(comodel_name="res.users")
    weighing_date = fields.Datetime()

    def _get_action_weighing_name(self):
        """Custom name to show in the wizard"""
        action_name = _(
            "Weigh %(product_uom_qty)s %(uom)s of %(product)s",
            product_uom_qty=self.product_uom_qty,
            uom=self.product_uom_id.name,
            product=self.product_id.name,
        )
        if self.lot_id:
            action_name += f" ({self.lot_id.name})"
        return action_name

    def action_weighing(self):
        """Open the wizard to record weights"""
        self.move_id.action_lock_weighing_operation()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_weighing.weighing_wizard_action"
        )
        action["name"] = self._get_action_weighing_name()
        action["context"] = dict(
            self.env.context,
            default_selected_move_line_id=self[0].id,
            default_weight=self[0].recorded_weight or self[0].qty_done,
            default_move_line_ids=self.ids,
            default_print_label=self.picking_type_id.print_weighing_label,
        )
        return action

    def action_print_weight_record_label(self):
        """Get detailed operations weighing labels"""
        return self.picking_type_id.weighing_label_report_id.report_action(self)

    def action_reset_weights(self):
        """Restore stock move lines weights"""
        self.qty_done = 0
        self.recorded_weight = 0
        self.has_recorded_weight = False
        # Keep who deleted them
        self.weighing_user_id = self.env.user
        self.weighing_date = fields.Datetime.now()
