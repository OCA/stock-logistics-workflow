# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    can_be_reassigned = fields.Boolean(
        compute="_compute_can_be_reassigned",
    )

    def _check_can_be_reassigned(self):
        if any(not picking.can_be_reassigned for picking in self):
            raise ValidationError(_("You cannot reassign moves that are not reserved!"))

    @api.depends("state")
    def _compute_can_be_reassigned(self):
        for picking in self:
            picking.can_be_reassigned = any(
                move.can_be_reassigned for move in picking.move_ids
            )

    def action_source_reassign(self):
        self._check_can_be_reassigned()
        context = self.env.context.copy()
        context["default_move_ids"] = self.move_ids.filtered("can_be_reassigned").ids
        if self.package_level_ids:
            context["default_package_level_ids"] = self.package_level_ids.filtered(
                "can_be_reassigned"
            ).ids
        # This can come from picking view context
        if "form_view_ref" in context:
            del context["form_view_ref"]
        return {
            "type": "ir.actions.act_window",
            "name": "Reassign",
            "res_model": "stock.move.reassign",
            "view_mode": "form",
            "target": "new",
            "context": context,
        }
