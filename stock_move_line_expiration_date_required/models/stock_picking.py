# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).


from odoo import _, exceptions, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _sanity_check(self, separate_pickings=True):
        res = super()._sanity_check(separate_pickings=separate_pickings)
        move_lines = self.env["stock.move.line"]
        # Batch validation considers processing across all pickings.
        has_pick = any(self.move_ids.mapped("picked"))
        for picking in self:
            if separate_pickings:
                # Individual validation considers only the current picking.
                has_pick = any(picking.move_ids.mapped("picked"))
            picking_move_lines = picking.move_line_ids.filtered("quantity")
            if has_pick:
                picking_move_lines = picking_move_lines.filtered("picked")
            move_lines |= picking_move_lines
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
