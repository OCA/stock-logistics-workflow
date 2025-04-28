# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    bypassed_reservation = fields.Boolean(
        string="Phantom reservation",
        help="Detailed operations with this flag, have a forced reserved quantity to "
        "reveal the uncovered demand in the system. It can be used to easily filter "
        "this operations",
    )

    def _action_done(self):
        # Allow to complete without reservation issues. These flagged move lines didn't
        # take their reserve from any quant, and they shouldn't unreserve from any
        # quant either.
        bypassed_mls = self.filtered("bypassed_reservation")
        super(
            StockMoveLine, bypassed_mls.with_context(force_bypass_reservation=True)
        )._action_done()
        return super(StockMoveLine, self - bypassed_mls)._action_done()

    def write(self, vals):
        # Allow to update without reservation issues. These flagged move lines didn't
        # take their reserve from any quant, and they shouldn't unreserve from any
        # quant either.
        bypassed_mls = self.filtered("bypassed_reservation")
        super(
            StockMoveLine, bypassed_mls.with_context(force_bypass_reservation=True)
        ).write(vals)
        return super(StockMoveLine, self - bypassed_mls).write(vals)

    def unlink(self):
        # Allow to unlink without reservation issues. These flagged move lines didn't
        # take their reserve from any quant, and they shouldn't unreserve from any
        # quant either.
        bypassed_mls = self.filtered("bypassed_reservation")
        super(
            StockMoveLine, bypassed_mls.with_context(force_bypass_reservation=True)
        ).unlink()
        return super(StockMoveLine, self - bypassed_mls).unlink()
