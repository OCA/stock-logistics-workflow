# Copyright 2024 ACSONE SA/NV
# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    # Prevent multiple lines for the same move and lot, otherwise it would
    # become very difficult to restrict the quantities per lot per move.
    _lot_id_move_id_uniq = models.Constraint(
        "UNIQUE(wizard_id, lot_id, move_id)",
        "The same lot cannot be used on multiple lines for the same move",
    )

    lot_id_domain = fields.Binary(compute="_compute_lot_id_domain")
    lot_id = fields.Many2one(
        "stock.lot", string="Lot/Serial Number", domain="lot_id_domain"
    )

    @api.depends("move_id")
    def _compute_lot_id_domain(self):
        for rec in self:
            if rec.move_id.company_id.stock_picking_return_lot_restrict:
                smls = rec.move_id.move_line_ids.filtered(
                    lambda x: x.state == "done" and x.lot_id
                )
                domain = [("id", "in", smls.lot_id.ids)]
            else:
                domain = [("product_id", "=", rec.product_id.id)]
            rec.lot_id_domain = domain

    def _prepare_move_default_values(self, new_picking):
        # Set the wizard line lot as the move's restricted lot
        vals = super()._prepare_move_default_values(new_picking)
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

    @api.constrains("lot_id")
    def _check_lot_id(self):
        # The restricted quantity can now depend on the lot
        return self._check_quantity()
