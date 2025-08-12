# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare, float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    progress = fields.Float(compute="_compute_progress", store=True, aggregator="avg")

    @api.depends(
        "product_uom_qty",
        "product_uom",
        "quantity",
        "state",
    )
    def _compute_progress(self):
        for record in self:
            if record.state == "done":
                record.progress = 100
                continue
            rounding = record.product_uom.rounding
            # If demanded quantity is effectively 0 then nothing
            # was asked to be moved, so it's 'completed' by definition.
            # Otherwise compute percent = done / demanded * 100.
            if float_is_zero(record.product_uom_qty, precision_rounding=rounding):
                record.progress = 100
            else:
                # We also need to keep in mind that the 'quantity' and 'product_uom_qty'
                # can be equal while the move is not done yet, for example
                # when transfer is ready to be processed (picking state is 'assigned').
                # In this case, we can wrongly consider the move as 100% done.
                # The idea is to have the move as 'almost done' in this case.
                percentage = (record.quantity / record.product_uom_qty) * 100
                # If percentage ever computes negative (bad data, returns, sign issues),
                # this forces it up to 0.0
                percentage = max(0.0, percentage)

                # Only moves that are 'done' can have a progress of 100%.
                if float_compare(percentage, 100.0, precision_digits=4) >= 0:
                    record.progress = 99.9  # aka 'almost done'
                else:
                    record.progress = min(99.9, percentage)
