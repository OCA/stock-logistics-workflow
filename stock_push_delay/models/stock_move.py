# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    location_final_id = fields.Many2one(
        "stock.location",
        "Final Location",
        readonly=False,
        store=True,
        help="The operation brings the products to the intermediate location."
        "But this operation is part of a chain of operations targeting the "
        "final location.",
        auto_join=True,
        index=True,
        check_company=True,
    )

    def _push_apply(self):
        """Manual triggering"""
        if self.env.context.get("manual_push", False):
            context = {}
            if self.location_final_id:
                context = {
                    "location_final_id": self.location_final_id.id,
                }
            new_move = super(StockMove, self.with_context(**context))._push_apply()
            if new_move:
                new_move._action_confirm()
            return new_move
        return self.env["stock.move"]
