# Copyright 2023 Ooops404
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class StockMove(models.Model):
    _inherit = "stock.move"

    change_restrict_lot = fields.Boolean(
        compute="_compute_change_restrict_lot",
        help="If the product is in the domain",
    )

    @api.depends("product_id", "company_id")
    def _compute_change_restrict_lot(self):
        for move in self:
            product_domain = safe_eval(
                move.sudo().company_id.enforce_lot_restriction_product_domain
            )
            # if product is not in the enforcement domain, user can change the lot
            move.change_restrict_lot = not move.product_id.filtered_domain(
                product_domain
            )

    def write(self, vals):
        """
        Propagate changes to restrict_lot_id to all
        destination moves - recursively.
        """
        res = super().write(vals)
        if "restrict_lot_id" in vals:
            related_moves = self.mapped("move_dest_ids")
            if related_moves:
                related_moves.write({"restrict_lot_id": vals["restrict_lot_id"]})
            self._action_assign()
        return res
