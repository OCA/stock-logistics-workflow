# Copyright 2020 Iryna Vyshnevska Camptocamp
# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import Command, api, fields, models

CONTEXT_KEY_FORCE_RECOMPUTE = "stock_picking_return_lot.force_recompute"


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    lots_visible = fields.Boolean(compute="_compute_lots_visible")

    @api.depends("product_return_moves.product_id.tracking")
    def _compute_lots_visible(self):
        """Only show the lots column in the wizard if applicable"""
        for wiz in self:
            wiz.lots_visible = any(
                tracking != "none"
                for tracking in wiz.product_return_moves.product_id.mapped("tracking")
            )

    def _get_qty_by_lot(self, move):
        """Get all quantities that were shipped out, per lot"""
        qties = defaultdict(float)
        for sml in move.move_line_ids:
            qties[sml.lot_id] += sml.quantity
        for dest_move in move.move_dest_ids:
            if dest_move.origin_returned_move_id == move:
                for sml in dest_move.move_line_ids:
                    qties[sml.lot_id] -= sml.quantity
        return qties

    def _compute_moves_locations(self):
        # Split up moves by tracked quantities. Lines are rebuilt with commands
        # instead of being copied, as this compute runs within onchange, where
        # real records would break the web client one2many diff.
        res = super()._compute_moves_locations()
        for wizard in self:
            product_return_moves = [Command.clear()]
            for line in wizard.product_return_moves:
                line_values = line.copy_data()[0]
                line_values.pop("wizard_id", None)
                qties = self._get_qty_by_lot(line.move_id)
                lot_qties = [(lot, qty) for lot, qty in qties.items() if qty > 0]
                if not lot_qties and qties:
                    # Everything has been returned already: keep a single line
                    # for the move, so it is still displayed in the wizard
                    lot_qties = [(next(iter(qties)), 0.0)]
                if not lot_qties:
                    product_return_moves.append(Command.create(line_values))
                    continue
                for lot, qty in lot_qties:
                    product_return_moves.append(
                        Command.create(dict(line_values, lot_id=lot.id, quantity=qty))
                    )
            wizard.product_return_moves = product_return_moves
        return res

    def _reset_quantities(self):
        """When asked to return all quantities, reset to restricted quantity per lot"""
        for wizard in self:
            for line in wizard.product_return_moves:
                line.quantity = line.get_returned_restricted_quantity(line.move_id)

    def action_create_returns_all(self):
        """Force a reset to returnable quantities per lot"""
        self = self.with_context(**{CONTEXT_KEY_FORCE_RECOMPUTE: True})
        return super().action_create_returns_all()

    def _create_return(self):
        """Propagate restricted lot, and reset quantities if requested"""
        if self.env.context.get(CONTEXT_KEY_FORCE_RECOMPUTE):
            self._reset_quantities()
        picking = super()._create_return()
        for ml in picking.move_line_ids:
            ml.lot_id = ml.move_id.restrict_lot_id
        return picking
