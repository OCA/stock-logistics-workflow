# Copyright 2023, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, models
from odoo.tools.float_utils import float_compare


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        if self._context.get("skip_difference_check", False):
            return super().button_validate()
        if any(
            float_compare(
                move.original_qty,
                move.quantity_done,
                precision_rounding=move.product_uom.rounding,
            )
            != 0
            for move in self.mapped("move_ids_without_package").filtered(
                lambda m: m.state not in ["cancel", "done"]
            )
        ):
            view_id = self.env.ref(
                "stock_picking_difference_warning."
                "picking_difference_warning_wizard_view_form"
            ).id
            return {
                "name": _("There are differences in the picking"),
                "view_mode": "form",
                "res_model": "picking.difference.warning.wizard",
                "type": "ir.actions.act_window",
                "target": "new",
                "view_id": view_id,
                "views": [(view_id, "form")],
                "context": {
                    "default_picking_ids": self.ids,
                },
            }
        return super().button_validate()
