# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import Command, _, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        for move in res:
            if move.product_id.cost_method != "fifo":
                continue
            if not move._is_in():
                continue
            for ml in move._get_in_move_lines():
                ml.qty_base = ml.product_uom_id._compute_quantity(
                    ml.qty_done, ml.product_id.uom_id
                )
        return res

    def _get_move_lots(self):
        self.ensure_one()
        correction_ml = self.env.context.get("correction_move_line")
        return correction_ml.lot_id if correction_ml else self.lot_ids

    def _prepare_common_svl_vals(self):
        """Add lots/serials to the stock valuation layer."""
        self.ensure_one()
        res = super()._prepare_common_svl_vals()
        lots = self._get_move_lots()
        res.update({"lot_ids": [Command.set(lots.ids)]})
        return res

    def _create_out_svl(self, forced_quantity=None):
        layers = self.env["stock.valuation.layer"]
        for move in self:
            # Set the move as a context for processing in _run_fifo().
            move = move.with_context(fifo_move=move)
            layer = super(StockMove, move)._create_out_svl(
                forced_quantity=forced_quantity
            )
            product = move.product_id
            # To prevent unknown creation of negative inventory.
            if (
                product.cost_method == "fifo"
                and product.tracking != "none"
                and layer.remaining_qty < 0
            ):
                raise UserError(
                    _("Negative inventory is not allowed for product %s.")
                    % product.display_name
                )
            layers |= layer
        return layers

    def _create_in_svl(self, forced_quantity=None):
        correction_ml = self.env.context.get("correction_move_line")
        if forced_quantity and correction_ml:
            correction_ml.qty_base += forced_quantity
            return super()._create_in_svl(forced_quantity=forced_quantity)
        layers = self.env["stock.valuation.layer"]
        for move in self:
            layer = super(StockMove, move)._create_in_svl(
                forced_quantity=forced_quantity
            )
            layers |= layer
            # Calculate standard price (sorted by lot created date)
            product = move.product_id
            if product.cost_method != "fifo" or product.tracking == "none":
                continue
            for ml in layer.stock_move_id.move_line_ids:
                ml.qty_base = ml.qty_done
            # Change product standard price to the first available lot price.
            product = product.with_context(sort_by="lot_create_date")
            candidate = product._get_fifo_candidates(move.company_id)[:1]
            if not candidate:
                continue
            product = product.with_company(move.company_id.id)
            product = product.with_context(disable_auto_svl=True)
            product.sudo().standard_price = candidate.unit_cost
        return layers

    def _get_price_unit(self):
        """No PO (e.g. customer returns) and get the price unit from the last consumed
        incoming move line for the lot.
        """
        self.ensure_one()
        if (
            not self.company_id.use_lot_cost_for_new_stock
            or self.product_id.cost_method != "fifo"
        ):
            return super()._get_price_unit()
        if hasattr(self, "purchase_line_id") and self.purchase_line_id:
            return super()._get_price_unit()
        lots = self._get_move_lots()
        if not len(lots) == 1:
            return super()._get_price_unit()
        # Get the most recent incoming move line for the lot.
        move_line = (
            self.env["stock.move.line"]
            .search(
                [
                    ("product_id", "=", self.product_id.id),
                    ("lot_id", "=", lots.id),
                    "|",
                    ("qty_consumed", ">", 0),
                    ("qty_remaining", ">", 0),
                    ("company_id", "=", self.company_id.id),
                ],
                order="id desc",
            )
            .filtered(lambda x: x.move_id._is_in())[:1]
        )
        if move_line:
            if move_line.qty_consumed:
                return move_line.value_consumed / move_line.qty_consumed
            return move_line.value_remaining / move_line.qty_remaining
        return super()._get_price_unit()
