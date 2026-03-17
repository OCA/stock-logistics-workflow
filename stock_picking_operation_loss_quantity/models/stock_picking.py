# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

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
