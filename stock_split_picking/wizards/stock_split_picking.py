# Copyright 2020 Hunki Enterprises BV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockSplitPicking(models.TransientModel):
    _name = "stock.split.picking"
    _description = "Split a picking"

    mode = fields.Selection(
        [
            ("done", "Done quantities"),
            ("move", "One picking per move"),
            (
                "available_line",
                (_("Split move lines between available and not available move lines")),
            ),
            (
                "available_product",
                (_("Split move lines between available and not available products")),
            ),
            ("selection", "Select move lines to split off"),
            (
                "split_product_quantities",
                (_("Split selected product and quantitites ")),
            ),
        ],
        required=True,
        default="done",
    )

    picking_ids = fields.Many2many(
        "stock.picking",
        default=lambda self: self._default_picking_ids(),
    )
    move_ids = fields.Many2many("stock.move")
    stock_split_product_quantities_ids = fields.One2many(
        "stock.split.product.quantities", "stock_split_picking_id"
    )

    def _default_picking_ids(self):
        return self.env["stock.picking"].browse(self.env.context.get("active_ids", []))

    def action_apply(self):
        return getattr(self, "_apply_%s" % self[:1].mode)()

    def _apply_done(self):
        return self.picking_ids.split_process("quantity_done")

    def _apply_move(self):
        """Create new pickings for every move line, keep first
        move line in original picking
        """
        new_pickings = self.env["stock.picking"]
        for picking in self.picking_ids:
            for move in picking.move_lines[1:]:
                new_pickings += picking._split_off_moves(move)
        return self._picking_action(new_pickings)

    def _apply_available_line(self):
        """Create different pickings for available and not available move line"""
        for picking in self.picking_ids:
            moves = picking.move_lines
            moves_available = moves.filtered(lambda move: move.state == "assigned")
            moves_available.picking_id._split_off_moves(moves_available)
        return self._picking_action(self.picking_ids)

    def _apply_available_product(self):
        """Create different pickings for available and not available move line"""
        return self.picking_ids.split_process("reserved_availability")

    def _apply_split_product_quantities(self):
        """Create different pickings with products and quantities selected"""
        for picking in self.picking_ids:
            moves = picking.move_lines
        split_list = [
            {"product_id": record.product_id, "qty": record.qty_to_split}
            for record in self.stock_split_product_quantities_ids
        ]
        new_picking = moves.picking_id._split_product_quantities(moves, split_list)
        return self._picking_action(new_picking)

    def _apply_selection(self):
        """Create one picking for all selected moves"""
        moves = self.move_ids
        new_picking = moves.picking_id._split_off_moves(moves)
        return self._picking_action(new_picking)

    def _picking_action(self, pickings):
        return pickings.get_formview_action() if pickings else False


class StockSplitProductQuantities(models.TransientModel):
    _name = "stock.split.product.quantities"
    _description = "Split a picking"

    stock_split_picking_id = fields.Many2one("stock.split.picking")
    product_id = fields.Many2one("product.product")
    qty_to_deliver = fields.Float(readonly=True)
    qty_to_split = fields.Float()
    product_ids = fields.Many2many(
        "product.product",
        default=lambda self: self._default_product_ids(),
    )

    def _default_product_ids(self):
        return (
            self.env["stock.picking"]
            .browse(self.env.context.get("active_ids", []))
            .move_lines.product_id
        )

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            picking_id = (
                self.env["stock.picking"]
                .browse(self.env.context.get("active_ids", []))
                .move_lines.filtered(lambda r: r.product_id == self.product_id)
            )
            self.qty_to_deliver = picking_id.product_uom_qty

    @api.onchange("qty_to_split")
    def onchange_qty_to_split(self):
        if self.qty_to_split > self.qty_to_deliver:
            raise UserError(
                _("Quantity to split can't be bigger than quantity to deliver")
            )
