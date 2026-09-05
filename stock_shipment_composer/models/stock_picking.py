# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    shipment_composer_ids = fields.Many2many(
        "stock.shipment.composer", compute="_compute_shipment_composer_ids"
    )

    def _compute_shipment_composer_ids(self):
        for rec in self:
            rec.shipment_composer_ids = rec.move_ids.shipment_composer_ids

    def button_validate(self):
        if self.env.context.get("validated_by_composer"):
            return super().button_validate()
        for rec in self:
            if rec.shipment_composer_ids.filtered(
                lambda x: x.state in ["in_progress", "draft"]
            ):
                raise UserError(
                    _(
                        "You cannot validate a transfer that has an active shipment "
                        "composer line. Please validate the shipment composer first."
                    )
                )
        return super().button_validate()

    @api.model
    def _get_action_view_shipment_composer(self, composers):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_shipment_composer.stock_shipment_composer_action"
        )
        if len(composers) > 1:
            action["domain"] = [("id", "in", composers.ids)]
        elif composers:
            action["views"] = [
                (
                    self.env.ref(
                        "stock_shipment_composer.stock_shipment_composer_form"
                    ).id,
                    "form",
                )
            ]
            action["res_id"] = composers.id
        return action

    def action_view_shipment_composers(self):
        return self._get_action_view_shipment_composer(self.shipment_composer_ids)
