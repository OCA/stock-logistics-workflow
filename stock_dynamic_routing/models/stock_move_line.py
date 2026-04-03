# Copyright 2026 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _log_message(self, record, move, template, vals):
        if self.env.context.get("bypass_log_message"):
            return
        super()._log_message(record, move, template, vals)
        return
