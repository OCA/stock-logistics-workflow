# Copyright 2023-2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, exceptions, fields, models


class StockProductSetWizard(models.TransientModel):
    _inherit = "product.set.wizard"
    _name = "stock.product.set.wizard"
    _description = "Wizard model to add product set into a picking form"

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

    def _compute_product_set_line_ids(self):
        res = super()._compute_product_set_line_ids()
        for rec in self:
            rec.product_set_line_ids = rec.product_set_id.set_line_ids.filtered(
                "product_id"
            )
        return res

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

    def _check_partner(self):
        res = super()._check_partner()
        if (
            self.product_set_id.partner_id
            and self.partner_id != self.product_set_id.partner_id
        ):
            raise exceptions.ValidationError(
                _("This set of products is restricted for this user.")
            )
        return res

    def add_set(self):
        res = super().add_set()
        if not self.picking_id:
            return res
        moves = self._prepare_stock_moves()
        if moves:
            self.picking_id.write({"move_ids_without_package": moves})
        return moves
