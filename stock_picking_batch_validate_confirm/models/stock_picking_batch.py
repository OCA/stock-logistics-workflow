# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    def action_done(self):
        self.ensure_one()
        if self.env.context.get("skip_batch_confirm"):
            return super().action_done()
        pending_orig_moves = self.move_ids.move_orig_ids.filtered_domain(
            [("state", "not in", ("cancel", "done"))]
        )
        if pending_orig_moves:
            return self._action_generate_batch_confirm_wizard()
        return super().action_done()

    def _action_generate_batch_confirm_wizard(self):
        return {
            "name": _("Batch Confirm"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "stock.picking.batch.confirm",
            "target": "new",
        }
