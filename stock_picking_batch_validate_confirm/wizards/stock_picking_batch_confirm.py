# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class StockPickingBatchConfirm(models.TransientModel):
    _name = "stock.picking.batch.confirm"
    _description = "Wizard Batch Confirm"

    batch_id = fields.Many2one("stock.picking.batch", string="Batch")
    move_ids = fields.Many2many("stock.move", string="Moves")

    def button_validate(self):
        return self.batch_id.with_context(skip_batch_confirm=True).action_done()
