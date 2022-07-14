# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_returned = fields.Float(
        compute="_compute_qty_returned",
        string="Returned Qty",
        store=True,
        readonly=True,
        compute_sudo=True,
        digits="Product Unit of Measure",
        default=0.0,
        copy=False,
    )

    @api.depends(
        "move_ids.state",
        "move_ids.scrapped",
        "move_ids.product_uom_qty",
        "move_ids.product_uom",
    )
    def _compute_qty_returned(self):
        for line in self:
            qty = 0.0
            if line.qty_delivered_method == "stock_move":
                _, incoming_moves = line._get_outgoing_incoming_moves()
                for move in incoming_moves:
                    if move.state != "done":
                        continue
                    qty += move.product_uom._compute_quantity(
                        move.product_uom_qty,
                        line.product_uom,
                        rounding_method="HALF-UP",
                    )
            line.qty_returned = qty
