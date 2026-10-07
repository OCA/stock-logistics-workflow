# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, float_round


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _check_can_split(self):
        self.ensure_one()
        product = self.product_id
        if self.state in ("done", "cancel"):
            raise UserError(
                self.env._(
                    "Move line for %(product)s cannot be split because its "
                    "transfer is already done or cancelled.",
                    product=product.display_name,
                )
            )
        if product.tracking == "serial":
            raise UserError(
                self.env._(
                    "Move line for %(product)s cannot be split: the product is "
                    "tracked by serial number.",
                    product=product.display_name,
                )
            )

    def _split_quantity(self, chunk_sizes):
        self.ensure_one()
        self._check_can_split()
        rounding = self.product_uom_id.rounding
        chunks = [
            float_round(size, precision_rounding=rounding)
            for size in chunk_sizes
            if not float_is_zero(size, precision_rounding=rounding)
        ]
        if len(chunks) <= 1:
            return self
        if float_compare(sum(chunks), self.quantity, precision_rounding=rounding) != 0:
            raise UserError(
                self.env._(
                    "The split quantities (%(split)s) do not add up to the "
                    "move line quantity (%(total)s) for %(product)s.",
                    split=sum(chunks),
                    total=self.quantity,
                    product=self.product_id.display_name,
                )
            )
        line_values = [self._prepare_split_line_values(chunk) for chunk in chunks]
        result = self
        self.write(line_values[0])
        for values in line_values[1:]:
            result |= self.copy(values)
        return result

    def _prepare_split_line_values(self, chunk):
        self.ensure_one()
        return {"quantity": chunk, "picked": self.picked}

    def action_open_split_wizard(self):
        if not self:
            raise UserError(self.env._("Select at least one move line to split."))
        return {
            "name": self.env._("Split Move Lines"),
            "type": "ir.actions.act_window",
            "res_model": "stock.move.line.split",
            "view_mode": "form",
            "target": "new",
            "context": dict(self.env.context, default_move_line_ids=[(6, 0, self.ids)]),
        }
