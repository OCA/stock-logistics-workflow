# Copyright 2020 Iryna Vyshnevska Camptocamp
# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import api, models
from odoo.tools.float_utils import float_round


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _get_qty_by_product_lot(self):
        res = defaultdict(float)
        for group in self.env["stock.move.line"].read_group(
            [
                ("picking_id", "=", self.picking_id.id),
                ("state", "=", "done"),
                ("move_id.scrapped", "=", False),
            ],
            ["quantity:sum"],
            ["move_id", "lot_id"],
            lazy=False,
        ):
            lot_id = group.get("lot_id")[0] if group.get("lot_id") else False
            move_id = group.get("move_id")[0]
            quantity = group.get("quantity")
            res[(move_id, lot_id)] += quantity
        return res

    @api.depends("picking_id")
    def _compute_moves_locations(self):
        res = super()._compute_moves_locations()
        product_return_moves = [(5,)]
        line_fields = [f for f in self.env["stock.return.picking.line"]._fields.keys()]
        product_return_moves_data_tmpl = self.env[
            "stock.return.picking.line"
        ].default_get(line_fields)
        qty_by_product_lot = self._get_qty_by_product_lot()
        for (move_id, lot_id), quantity in qty_by_product_lot.items():
            product_return_moves_data = dict(product_return_moves_data_tmpl)
            product_return_moves_data.update(
                self._prepare_stock_return_picking_line_vals(move_id, lot_id, quantity)
            )
            product_return_moves.append((0, 0, product_return_moves_data))
        if self.picking_id:
            self.product_return_moves = product_return_moves
        return res

    @api.model
    def _prepare_stock_return_picking_line_vals(self, move_id, lot_id, quantity):
        move = self.env["stock.move"].browse(move_id)
        quantity = quantity
        for dest_move in move.move_dest_ids:
            if (
                not dest_move.origin_returned_move_id
                or dest_move.origin_returned_move_id != move
            ):
                continue

            if (
                dest_move.restrict_lot_id
                and dest_move.restrict_lot_id.id == lot_id
                or not lot_id
            ):
                if dest_move.state in ("partially_available", "assigned"):
                    quantity -= sum(dest_move.move_line_ids.mapped("quantity"))
                elif dest_move.state == "done":
                    quantity -= dest_move.product_qty
        quantity = float_round(
            quantity, precision_rounding=move.product_id.uom_id.rounding
        )
        return {
            "product_id": move.product_id.id,
            "quantity": quantity,
            "move_id": move.id,
            "uom_id": move.product_id.uom_id.id,
            "lot_id": lot_id,
        }

    def _prepare_move_default_values(self, return_line, new_picking):
        vals = super()._prepare_move_default_values(return_line, new_picking)
        vals["restrict_lot_id"] = return_line.lot_id.id
        return vals

    def _create_returns(self):
        res = super()._create_returns()
        picking_returned = self.env["stock.picking"].browse(res[0])
        for ml in picking_returned.move_line_ids:
            ml.lot_id = ml.move_id.restrict_lot_id
        return res
