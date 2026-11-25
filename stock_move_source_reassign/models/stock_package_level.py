# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPackageLevel(models.Model):

    _inherit = "stock.package_level"

    can_be_reassigned = fields.Boolean(
        compute="_compute_can_be_reassigned",
    )

    @api.depends("move_line_ids.move_id.state")
    def _compute_can_be_reassigned(self):
        for level in self:
            if (
                not self.env.user.has_group(
                    "stock_move_source_reassign.group_can_reassign"
                )
                or (not level.picking_id.picking_type_id.can_reassign)
                or (
                    not level.move_line_ids
                    or any(move.state != "assigned" for move in level.move_ids)
                )
            ):
                level.can_be_reassigned = False
            else:
                level.can_be_reassigned = True

    def _check_can_be_reassigned(self):
        if any(not level.can_be_reassigned for level in self):
            raise ValidationError(
                _("You cannot reassign packages that are not reserved!")
            )

    def action_source_reassign(self):
        self._check_can_be_reassigned()
        context = self.env.context.copy()
        context["default_move_ids"] = self.move_line_ids.move_id.ids
        context["default_package_level_ids"] = self.ids
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
