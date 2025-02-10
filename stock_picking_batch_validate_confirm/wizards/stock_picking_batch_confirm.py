# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class StockPickingBatchConfirm(models.TransientModel):
    _name = "stock.picking.batch.confirm"
    _description = "Wizard Batch Confirm"

    batch_id = fields.Many2one(
        "stock.picking.batch",
        string="Batch",
        required=True,
        default=lambda self: self._default_batch_id(),
    )
    move_ids = fields.Many2many(
        "stock.move", string="Moves", compute="_compute_move_ids"
    )

    @api.model
    def _default_batch_id(self):
        """Get batch from context."""
        if self.env.context.get("active_model") == "stock.picking.batch":
            return self.env.context.get("active_id")

    @api.depends("batch_id")
    def _compute_move_ids(self):
        """Get moves from batch."""
        for wizard in self:
            wizard.move_ids = wizard.batch_id.move_ids.move_orig_ids.filtered_domain(
                [("state", "not in", ("cancel", "done"))]
            )

    def button_validate(self):
        return self.batch_id.with_context(skip_batch_confirm=True).action_done()
