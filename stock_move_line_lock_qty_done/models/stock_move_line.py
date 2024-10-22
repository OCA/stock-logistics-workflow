# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    def _check_qty_done_change_allowed(self, vals):
        if vals.get("qty_done", None) is None:
            return True
        has_group = self.env.user.has_group(
            "stock_move_line_lock_qty_done.group_stock_move_can_edit_done_qty"
        )
        for rec in self:
            if rec.state != "done":
                continue
            if rec.is_locked:
                raise UserError(
                    _(
                        "This move is locked, you can't edit the done quantity unless "
                        "you unlock it"
                    )
                )
            if not has_group:
                raise UserError(
                    _("You are not allowed to change the quantity done for done moves")
                )

    def write(self, vals):
        self._check_qty_done_change_allowed(vals)
        return super().write(vals)
