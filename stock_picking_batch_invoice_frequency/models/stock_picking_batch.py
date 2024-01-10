# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    def action_done(self):
        if not self.env.context.get("invoice_batch", False):
            return super().with_context(invoice_batch=True).action_done()
        return super().action_done()
