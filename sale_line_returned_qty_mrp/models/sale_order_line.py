# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "move_ids.state",
        "move_ids.scrapped",
        "move_ids.product_uom_qty",
        "move_ids.product_uom",
    )
    def _compute_qty_returned(self):
        # Based on the standard method in 'sale_mrp' to compute qty_delivered
        super(SaleOrderLine, self)._compute_qty_returned()
        for order_line in self:
            if order_line.qty_delivered_method == "stock_move":
                boms = order_line.move_ids.filtered(
                    lambda m: m.state != "cancel"
                ).mapped("bom_line_id.bom_id")
                dropship = any([m._is_dropshipped() for m in order_line.move_ids])
                if not boms and dropship:
                    boms = boms._bom_find(
                        product=order_line.product_id,
                        company_id=order_line.company_id.id,
                        bom_type="phantom",
                    )
                relevant_bom = boms.filtered(
                    lambda b: b.type == "phantom"
                    and (
                        b.product_id == order_line.product_id
                        or (
                            b.product_tmpl_id == order_line.product_id.product_tmpl_id
                            and not b.product_id
                        )
                    )
                )
                if relevant_bom:
                    if dropship:
                        moves = order_line.move_ids.filtered(
                            lambda m: m.state != "cancel"
                        )
                        if any(
                            (
                                m.location_dest_id.usage != "customer"
                                and m.state == "done"
                                and float_compare(
                                    m.quantity_done,
                                    sum(
                                        sub_m.product_uom._compute_quantity(
                                            sub_m.quantity_done, m.product_uom
                                        )
                                        for sub_m in m.returned_move_ids
                                        if sub_m.state == "done"
                                    ),
                                    precision_rounding=m.product_uom.rounding,
                                )
                                > 0
                            )
                            for m in moves
                        ):
                            order_line.qty_returned = order_line.product_uom_qty
                        else:
                            order_line.qty_returned = 0.0
                        continue
                    moves = order_line.move_ids.filtered(
                        lambda m: m.state == "done" and not m.scrapped
                    )
                    filters = {
                        "incoming_moves": lambda m: m.location_dest_id.usage
                        != "customer"
                        and m.to_refund,
                        "outgoing_moves": lambda m: False,
                    }
                    order_qty = order_line.product_uom._compute_quantity(
                        order_line.product_uom_qty, relevant_bom.product_uom_id
                    )
                    qty_returned = moves._compute_kit_quantities(
                        order_line.product_id, order_qty, relevant_bom, filters
                    )
                    order_line.qty_returned = relevant_bom.product_uom_id._compute_quantity(
                        qty_returned, order_line.product_uom
                    )
                elif boms:
                    if all(
                        [
                            m.state == "done" and m.location_dest_id.usage == "customer"
                            for m in order_line.move_ids
                        ]
                    ):
                        order_line.qty_returned = 0.0
                    else:
                        order_line.qty_returned = order_line.product_uom_qty
