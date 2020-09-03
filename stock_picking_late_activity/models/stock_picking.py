# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _cron_late_picking_activity(self):
        """Create an activity for late pickings."""
        late_picking = self.search([
            ("state", 'not in', ["draft", "done", "cancel"]),
            ("picking_type_id.create_late_picking_activity", '=', True),
            ("scheduled_date", '<', datetime.now()),
        ])
        if not late_picking:
            return False
        activity_type = self.env.ref(
            "stock_picking_late_activity"
            ".mail_activity_type_update_scheduled_date")
        vals_list = []
        for picking in late_picking:
            if not bool(picking.activity_ids.filtered(
                    lambda r: r.activity_type_id == activity_type)):
                vals_list.append(picking._prepare_late_picking_activity_vals())
        self.env["mail.activity"].create(vals_list)

    def _prepare_late_picking_activity_vals(self):
        """ Hook method to prepare the values to create a late picking
        activity.
        """
        self.ensure_one()
        activity_type = self.env.ref(
            "stock_picking_late_activity"
            ".mail_activity_type_update_scheduled_date")
        return {
            "res_id": self.id,
            "res_model_id": self.env.ref("stock.model_stock_picking").id,
            "activity_type_id": activity_type.id,
            "summary": activity_type.summary,
            "note": activity_type.summary,
            "automated": True,
            "user_id": self.picking_type_id.late_picking_activity_user_id.id,
        }
