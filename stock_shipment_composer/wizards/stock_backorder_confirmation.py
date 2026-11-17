# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


class StockBackorderConfirmation(models.TransientModel):
    _inherit = "stock.backorder.confirmation"

    def _prepare_composer_moves(self):
        composer_id = self.env.context.get("validated_by_composer")
        if composer_id:
            composer = self.env["stock.shipment.composer"].browse(composer_id)
            composer._prepare_moves_for_validation()

    def process(self):
        self._prepare_composer_moves()
        return super().process()

    def process_cancel_backorder(self):
        self._prepare_composer_moves()
        return super().process_cancel_backorder()
