# Copyright (C) 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    excess_quantity = fields.Float(
        help="Quantity received beyond the original demand",
        copy=False,
    )

    def _create_extra_move(self):
        """Override to check if extra moves are disabled on the picking type.
        If disabled, store excess quantity and return self without creating extra moves.
        """
        # Check if extra moves are disabled for this picking type
        if self.picking_id and self.picking_id.picking_type_id.disable_extra_moves:
            # Store the excess quantity if any
            rounding = self.product_uom.rounding
            if (
                float_compare(
                    self.quantity, self.product_uom_qty, precision_rounding=rounding
                )
                > 0
            ):
                excess = self.quantity - self.product_uom_qty
                self.excess_quantity = excess
                # Return empty recordset to prevent extra move creation
                # but excess quantity is stored on the original move
                return self.browse()

            # No excess quantity, return self as normal
            return self

        # Use the original logic if extra moves are not disabled
        return super()._create_extra_move()
