# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class MassMrpProductionOrderWizard(models.TransientModel):
    _inherit = "mrp.mass.production.order.wizard"

    def action_create(self):
        picking = None
        if (
            "active_model" in self.env.context
            and self.env.context["active_model"] == "stock.picking"
        ):
            picking = self.env["stock.picking"].browse(self.env.context["active_id"])
            picking_products = set(picking.move_ids.mapped("product_id"))
            if self.with_bom:
                for entry in self.mrp_production_order_entries:
                    bom_products = set(entry.bom_id.bom_line_ids.mapped("product_id"))
                    if not bom_products.issubset(picking_products):
                        raise ValidationError(
                            _(
                                "All products from BOM '{bom}' "
                                "must exist in the picking lines."
                            ).format(bom=entry.bom_id.display_name)
                        )
                for entry in self.mrp_production_order_entries:
                    for bom_line_id in entry.bom_id.bom_line_ids:
                        scraps = self.env["stock.scrap"].search(
                            [
                                ("picking_id", "=", picking.id),
                                ("product_id", "=", bom_line_id.product_id.id),
                            ]
                        )
                        sum_scraps = sum(scraps.mapped("scrap_qty"))
                        moves = picking.move_ids.filtered(
                            lambda x, bom_line_id=bom_line_id: x.product_id
                            == bom_line_id.product_id
                            and x.product_uom_qty > 0
                            and x.consumed_quantity < x.product_uom_qty
                        )
                        sum_moves_qty = sum(moves.mapped("product_uom_qty"))
                        sum_moves_qty_cons = sum(moves.mapped("consumed_quantity"))

                        quantity = entry.product_qty * bom_line_id.product_qty

                        if quantity + sum_moves_qty_cons > sum_moves_qty - sum_scraps:
                            self.raise_error_qty_to_consume(
                                quantity,
                                sum_moves_qty,
                                sum_scraps,
                                sum_moves_qty_cons,
                                bom_line_id.product_id,
                            )
                        self.consume_products(moves, sum_scraps, quantity)
            else:
                for entry in self.mrp_production_order_entries:
                    if entry.product_consumed_id not in picking_products:
                        raise ValidationError(
                            _(
                                "Consumed product '{prod}' is not present "
                                "in the picking lines."
                            ).format(prod=entry.product_consumed_id.display_name)
                        )
                for entry in self.mrp_production_order_entries:
                    scraps = self.env["stock.scrap"].search(
                        [
                            ("picking_id", "=", picking.id),
                            ("product_id", "=", entry.product_consumed_id.id),
                        ]
                    )

                    sum_scraps = sum(scraps.mapped("scrap_qty"))
                    moves = picking.move_ids.filtered(
                        lambda x, entry=entry: x.product_id == entry.product_consumed_id
                        and x.product_uom_qty > 0
                        and x.consumed_quantity < x.product_uom_qty
                    )
                    sum_moves_qty = sum(moves.mapped("product_uom_qty"))
                    sum_moves_qty_cons = sum(moves.mapped("consumed_quantity"))

                    if entry.quantity + sum_moves_qty_cons > sum_moves_qty - sum_scraps:
                        self.raise_error_qty_to_consume(
                            entry.quantity,
                            sum_moves_qty,
                            sum_scraps,
                            sum_moves_qty_cons,
                            entry.product_consumed_id,
                        )
                    self.consume_products(moves, sum_scraps, entry.quantity)

        res = super().action_create()
        if picking:
            self.link_mrp_production_orders(picking, res)
        return res

    def raise_error_qty_to_consume(
        self, quantity, sum_moves_qty, sum_scraps, sum_moves_qty_cons, product
    ):
        raise ValidationError(
            _(
                "Quantity to consume ({qty}) is greater than the "
                "quantity of the stock moves "
                "({uom_qty}) for product '{prod}'"
            ).format(
                qty=quantity,
                uom_qty=sum_moves_qty - sum_scraps - sum_moves_qty_cons,
                prod=product.display_name,
            )
        )

    def consume_products(self, moves, sum_scraps, quantity):
        quantity_to_consume = quantity + sum_scraps
        # Calculate the net quantity that *must* be consumed from the moves
        qty_remaining_to_consume = quantity_to_consume - sum_scraps
        for move in moves:
            # Quantity still available on the current move
            qty_available_on_move = move.product_uom_qty - move.consumed_quantity
            # Check if the move has any available quantity to consume
            if qty_available_on_move > 0:
                # The amount to consume is the MINIMUM of what we still need
                # and what the current move can provide.
                consumption_amount = min(
                    qty_remaining_to_consume, qty_available_on_move
                )
                # 1. Update the consumed quantity on the current move
                move.consumed_quantity += consumption_amount
                # 2. Reduce the total remaining quantity to consume
                qty_remaining_to_consume -= consumption_amount
                # 3. If we have satisfied the total required consumption, stop iterating
                if qty_remaining_to_consume <= 0:
                    break

    def link_mrp_production_orders(self, picking, res):
        mrp_ids = self.env["mrp.production"].browse(res["domain"][0][2])
        if mrp_ids:
            matching_mrps = mrp_ids.filtered(
                lambda mrp: any(
                    move.product_id in picking.move_ids.mapped("product_id")
                    for move in mrp.move_raw_ids
                )
            )
            if matching_mrps:
                picking.mrp_picking_ids = [(4, mrp.id) for mrp in matching_mrps]
