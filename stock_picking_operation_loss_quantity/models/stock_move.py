# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.fields import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _try_reallocate_loss_qty(self, ignored_quant_ids=False):
        """Keep the picking going when a loss is reported.

        Looks for the missing items in other stock locations
        so the picker can still finish their job.

        ignored_quant_ids: the ids of the quants to ignore for re-reservation
        """
        self.ensure_one()
        if (
            float_compare(
                self.product_uom_qty,
                self.reserved_availability,
                precision_rounding=self.product_uom.rounding,
            )
            > 0
        ):
            self.with_context(
                _loss_ignored_quant_ids=ignored_quant_ids
            )._action_assign()
