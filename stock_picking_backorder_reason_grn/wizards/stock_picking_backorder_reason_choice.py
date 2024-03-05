# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockBackorderReasonChoice(models.TransientModel):

    _inherit = "stock.backorder.reason.choice"

    def _prepare_backorder_confirmation_line(self, picking):
        res = super()._prepare_backorder_confirmation_line(picking)
        res.update(
            {
                "keep_grn": self.reason_id.keep_grn,
            }
        )
        return res
