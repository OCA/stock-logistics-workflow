# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    loss_declaration_count = fields.Integer(
        string="Number of Loss Declarations", default=0, copy=False
    )

    is_loss_picking = fields.Boolean(compute="_compute_is_loss_picking")

    def _compute_is_loss_picking(self):
        for rec in self:
            rec.is_loss_picking = (
                rec.picking_type_id.id
                == rec.picking_type_id.warehouse_id.loss_type_id.id
            )

    def _schedule_loss_activity(self):
        self.ensure_one()
        group = self.env.ref(
            "stock_picking_operation_loss_quantity.group_loss_notification",
            raise_if_not_found=False,
        )
        if not group:
            return
        for user in group.users:
            self.activity_schedule(
                act_type_xmlid="stock_picking_operation_loss_quantity.\
                    loss_picking_notification",
                summary=self.name,
                user_id=user.id,
            )
