# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    _sql_constraints = [
        # Prevent multiple lines for the same move and lot, otherwise it would
        # become very difficult to restrict the quantities per lot per move.
        (
            "lot_id_move_id_uniq",
            "UNIQUE(wizard_id, lot_id, move_id)",
            "The same lot cannot be used on multiple lines for the same move",
        )
    ]

    lot_id = fields.Many2one(
        "stock.lot",
        string="Lot/Serial Number",
        domain="[('product_id', '=', product_id)]",
    )

    def _prepare_move_default_values(self, picking):
        # Set the wizard line lot as the move's restricted lot
        vals = super()._prepare_move_default_values(picking)
        vals["restrict_lot_id"] = self.lot_id.id
        return vals

    @api.model
    def get_returned_restricted_quantity(self, stock_move):
        """Get the restricted quantity by lot (if any).

        Overwrite of this method from stock_picking_return_restricted_qty.
        This module calls this method with either zero or one record(s) in
        `self`, and does not use the actual value of `self`. For our purposes,
        we want to use the value of `lot_id` in self as an additional filter
        (and using an empty value for `lot_id` should work fine in case `self`
        is not set).
        """
        if self:
            self.ensure_one()
        return sum(
            stock_move.move_line_ids.filtered(
                lambda sml: sml.lot_id == self.lot_id
            ).mapped("quantity")
        ) - sum(
            stock_move.move_dest_ids.filtered(
                lambda sm: sm.origin_returned_move_id == stock_move
            )
            .move_line_ids.filtered(lambda sml: sml.lot_id == self.lot_id)
            .mapped("quantity")
        )

    @api.onchange("quantity", "lot_id")
    def _onchange_quantity(self):
        # The restricted quantity can now depend on the lot
        return super()._onchange_quantity()
