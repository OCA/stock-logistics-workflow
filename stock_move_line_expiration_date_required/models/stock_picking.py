# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).


from odoo import _, exceptions, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _sanity_check(self, separate_pickings=True):
        """Sanity check for expiration dates."""
        res = super()._sanity_check()
        for picking in self:
            move_lines = self.env["stock.move.line"].browse()
            for move in picking.move_ids:
                # For assigned moves
                move_lines |= move._get_move_lines()
            move_lines_wo_expiration_date = move_lines.filtered_domain(
                [
                    ("use_expiration_date", "=", True),
                    ("expiration_date", "=", False),
                ]
            )
            if move_lines_wo_expiration_date:
                raise exceptions.UserError(
                    _(
                        "The following move lines have no expiration date: %s",
                        ", ".join(move_lines_wo_expiration_date.mapped("display_name")),
                    )
                )
        return res
