# Copyright 2024 Cetmix OU
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
        if not self._check_return_limit_enforcement():
            return
        for rec in self:
            if rec.quantity and rec.quantity_max and rec.quantity > rec.quantity_max:
                raise ValidationError(
                    _(
                        "You can return only %(max_qty)s of %(product)s",
                        max_qty=rec.quantity_max,
                        product=rec.product_id.name,
                    )
                )

    @api.model
    def _check_return_limit_enforcement(self):
        """Returns the state of the "Stock Picking Return Quantity Limit" option

        Returns:
            bool: Option status
        """
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "stock_picking_limit_return_qty.stock_picking_limit_return_qty", False
            )
        )
