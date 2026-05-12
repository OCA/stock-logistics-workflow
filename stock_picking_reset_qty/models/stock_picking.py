# Copyright 2026 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_clear_qty(self):
        self.ensure_one()
        self.move_ids.filtered(lambda m: m.state not in ("done", "cancel")).write(
            {"quantity": 0}
        )
