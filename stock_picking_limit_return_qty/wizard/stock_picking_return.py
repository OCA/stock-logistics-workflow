# Copyright 2023 Cetmix OU
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    quantity_max = fields.Float(
        "Maximum Quantity",
        digits="Product Unit of Measure",
        help="Maximum quantity that can be returned",
    )

    @api.constrains("quantity")
    def _constraints_quantity(self):
        for rec in self:
            if rec.quantity and rec.quantity_max and rec.quantity > rec.quantity_max:
                raise ValidationError(
                    _(
                        "You can return only %(max_qty)s of %(product)s",
                        max_qty=rec.quantity_max,
                        product=rec.product_id.name,
                    )
                )


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):

        res = super(
            ReturnPicking, self
        )._prepare_stock_return_picking_line_vals_from_move(stock_move)

        # Store maximum quantity that is possible to return
        res.update(
            {
                "quantity_max": res["quantity"],
            }
        )
        return res
