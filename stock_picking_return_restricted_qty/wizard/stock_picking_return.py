# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        val = super()._prepare_stock_return_picking_line_vals_from_move(stock_move)
        return_lines = self.env["stock.return.picking.line"]
        val["quantity"] = return_lines.get_returned_restricted_quantity(stock_move)
        return val

    def _create_returns(self):
        restrict_return_qty = self.picking_id.picking_type_id.restrict_return_qty

        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for return_line in self.product_return_moves:
            quantity = return_line.get_returned_restricted_quantity(return_line.move_id)

            if restrict_return_qty and (
                float_compare(
                    return_line.quantity, quantity, precision_digits=precision
                )
                > 0
            ):
                raise UserError(
                    _("Return more quantities than delivered is not allowed.")
                )
        return super()._create_returns()


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    @api.onchange("quantity")
    def _onchange_quantity(self):
        restrict_return_qty = (
            self.move_id.picking_id.picking_type_id.restrict_return_qty
        )

        qty = self.get_returned_restricted_quantity(self.move_id)

        if restrict_return_qty and self.quantity > qty:
            raise UserError(_("Return more quantities than delivered is not allowed."))

    def get_returned_restricted_quantity(self, stock_move):
        """This function is created to know how many products
        have the person who tries to create a return picking
        on his hand."""
        qty = stock_move.product_qty
        for line in stock_move.move_dest_ids.mapped("move_line_ids"):
            if (
                line.move_id.origin_returned_move_id
                and line.move_id.origin_returned_move_id != stock_move
            ):
                continue
            if line.state in {"partially_available", "assigned", "done"}:
                qty -= line.quantity
        # Quantities consumed by a chained destination move (e.g. a delivery
        # linked to the receipt through MTO) that came back to us through a
        # return of that destination move are on hand again, so they can be
        # returned too.
        chained_moves = stock_move.move_dest_ids.filtered(
            lambda m: not m.origin_returned_move_id
        )
        for returned_move in chained_moves.returned_move_ids:
            qty += self._get_net_returned_quantity(returned_move)
        return max(qty, 0.0)

    @api.model
    def _get_net_returned_quantity(self, returned_move):
        """Quantity of a done return move, minus what was sent again through
        returns of that return."""
        if returned_move.state != "done":
            return 0.0
        qty = returned_move.product_qty
        for move in returned_move.returned_move_ids:
            qty -= self._get_net_returned_quantity(move)
        return max(qty, 0.0)
