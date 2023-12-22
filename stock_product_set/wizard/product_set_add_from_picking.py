# Copyright 2023-2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ProductSetAddFromPicking(models.TransientModel):
    _inherit = "product.set.add"
    _name = "product.set.add.from.picking"
    _description = "product.set.add.from.picking"

    order_id = fields.Many2one(required=False)
    picking_id = fields.Many2one(
        comodel_name="stock.picking",
        string="Picking",
        required=True,
        default=lambda self: self.env.context.get("active_id")
        if self.env.context.get("active_model") == "stock.picking"
        else None,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(related="picking_id.partner_id", ondelete="cascade")

    def _prepare_stock_moves(self):
        moves = []
        for _seq, set_line in enumerate(self._get_lines(), start=1):
            values = self.prepare_stock_move_data(set_line)
            moves.append((0, 0, values))
        return moves

    def prepare_stock_move_data(self, set_line):
        self.ensure_one()
        return set_line.prepare_picking_stock_move_values(
            self.picking_id, self.quantity
        )

    def add_set(self):
        if not self.picking_id:
            return super().add_set()
        self._check_partner()
        moves = self._prepare_stock_moves()
        if moves:
            self.picking_id.write({"move_ids_without_package": moves})
        return moves
