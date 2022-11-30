# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    def _prepare_move_split_vals(self, qty, move_id):
        """ Values to be set in the new move line.
            We set the qty_done so the new line keeps the done quantities.
        """
        vals = {
            "product_uom_qty": qty,
            "qty_done": self.qty_done,
            "move_id": move_id,
        }
        if self.env.context.get("force_split_uom_id"):
            vals["product_uom_id"] = self.env.context["force_split_uom_id"]
        return vals

    def _get_original_move_vals(self, qty):
        decimal_precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        new_product_qty = self.product_id.uom_id._compute_quantity(
            self.product_qty - qty, self.product_uom_id, round=False
        )
        new_product_qty = float_round(
            new_product_qty, precision_digits=decimal_precision
        )
        return {
            "product_uom_qty": new_product_qty,
            "qty_done": 0.0,
        }

    def _split(self, qty, move_id):
        """ Splits a stock move line with a defined qty and move to a new stock move

        :param qty: float. quantity to split (given in product UoM)
        :returns: id of the backorder move line created """
        self.ensure_one()
        self = self.with_prefetch()
        # This makes the ORM only look for one record and not 300 at a time,
        # which improves performance
        if self.state in ("done", "cancel"):
            raise UserError(
                _("You cannot split a stock move line that has been set to 'Done'.")
            )
        elif self.state == "draft":
            # we restrict the split of a draft line because if not confirmed yet.
            raise UserError(
                _("You cannot split a draft line. It needs to be confirmed first.")
            )
        if (
            float_is_zero(qty, precision_rounding=self.product_id.uom_id.rounding)
            or self.product_qty <= qty
        ):
            self.move_id = move_id
            return self.id

        decimal_precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )

        # `qty` passed as argument is the quantity to backorder and is always expressed in the
        # quants UOM.
        uom_qty = self.product_id.uom_id._compute_quantity(
            qty, self.product_uom_id, rounding_method="HALF-UP"
        )
        # TODO: usamos precision_digits porque le copiamos a odoo con stock move,
        #  pero quizás debería ser: precision_rounding=self.product_id.uom_id.rounding
        if (
            float_compare(
                qty,
                self.product_uom_id._compute_quantity(
                    uom_qty, self.product_id.uom_id, rounding_method="HALF-UP"
                ),
                precision_digits=decimal_precision,
            )
            == 0
        ):
            defaults = self._prepare_move_split_vals(uom_qty, move_id)
        else:
            defaults = self.with_context(
                force_split_uom_id=self.product_id.uom_id.id
            )._prepare_move_split_vals(qty, move_id)

        ml = self.with_context(rounding_method="HALF-UP").copy(defaults)
        self.write(self._get_original_move_vals(qty))

        # We need to update quants reservations because it is not
        # properly updated when copy a line
        self.env["stock.quant"]._update_reserved_quantity(
            ml.product_id,
            ml.location_id,
            ml.product_qty,
            lot_id=ml.lot_id,
            package_id=ml.package_id,
            owner_id=ml.owner_id,
            strict=True,
        )
        return ml.id
