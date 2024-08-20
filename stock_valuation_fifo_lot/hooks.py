# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import SUPERUSER_ID, api
from odoo.tools import float_is_zero


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    moves = env["stock.move"].search([("stock_valuation_layer_ids", "!=", False)])
    for move in moves:
        if (
            move.product_id.with_company(move.company_id).cost_method != "fifo"
            or not move.lot_ids
        ):
            continue
        svls = move.stock_valuation_layer_ids
        svls.lot_ids = move.lot_ids
        if move._is_out():
            remaining_qty = sum(svls.mapped("remaining_qty"))
            if remaining_qty:
                # The case where outgoing done qty is reduced
                # Let the first move line take such adjustments.
                move.move_line_ids[0].qty_base = remaining_qty
            continue
        consumed_qty = consumed_qty_bal = sum(svls.mapped("quantity")) - sum(
            svls.mapped("remaining_qty")
        )
        total_value = sum(svls.mapped("value")) + sum(
            svls.stock_valuation_layer_ids.mapped("value")
        )
        consumed_value = total_value - sum(svls.mapped("remaining_value"))
        product_uom = move.product_id.uom_id
        for ml in move.move_line_ids.sorted("id"):
            ml.qty_base = ml.product_uom_id._compute_quantity(ml.qty_done, product_uom)
            if float_is_zero(consumed_qty_bal, precision_rounding=product_uom.rounding):
                continue
            qty_to_allocate = min(consumed_qty_bal, ml.qty_base)
            ml.qty_consumed += qty_to_allocate
            consumed_qty_bal -= qty_to_allocate
            ml.value_consumed += consumed_value * qty_to_allocate / consumed_qty
