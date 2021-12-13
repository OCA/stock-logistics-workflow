# Copyright 2021 Hunki Enterprises BV
# Copyright 2021 Opener B.V. <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero


class StockPicking(models.Model):
    _inherit = "stock.picking"

    use_manual_lot_selection = fields.Boolean(
        related="picking_type_id.use_manual_lot_selection",
    )

    def button_validate(self):
        """Check for missing manually assigned lots"""
        if self.picking_type_id.use_manual_lot_selection:
            precision_digits = self.env['decimal.precision'].precision_get(
                'Product Unit of Measure')
            no_quantities_done = all(
                float_is_zero(move_line.qty_done,
                              precision_digits=precision_digits)
                for move_line in self.move_line_ids.filtered(
                    lambda m: m.state not in ('done', 'cancel')))
            lines_to_check = self.move_line_ids
            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(
                    lambda line: float_compare(
                        line.qty_done, 0,
                        precision_rounding=line.product_uom_id.rounding)
                )
            missing = lines_to_check.filtered(
                lambda line: line.product_id.tracking != 'none'
                and not line.manual_lot_id).mapped("product_id")
            if missing:
                raise UserError(
                    _('Please supply a Lot/Serial number for products %s.') %
                    ", ".join(product.name or product.default_code
                              for product in missing))
        return super().button_validate()

    def action_done(self):
        """Keep manual lots up to date not to lose visibility.

        Keep visibility of transferred lot in the case of
        * an untracked product transferred without setting a manual lot
        * an update of a picking type to use manual lot selection
        """
        res = super().action_done()
        for ml in self.mapped("move_line_ids").filtered(
                lambda ml: ml.lot_id != ml.manual_lot_id):
            ml.manual_lot_id = ml.lot_id
        return res

    def write(self, vals):
        """Encode move line quantities in the context if necessary.

        If manual_lot_id is being written on the move lines, this could lead
        to freeing move lines from the same picking that are also being
        written in this very same call. We encode the original reserved
        quantities of the move lines in the context so that they can be
        rereserved for these quantities.
        """
        StockMoveLine = self.env['stock.move.line']
        defer_delete_lines = StockMoveLine.browse([])
        explicit_delete_lines = StockMoveLine.browse([])
        writes_manual_lot_id = False
        for command in (vals.get("move_line_ids", []) or []) + (
                vals.get("move_line_ids_without_package", []) or []
        ):
            if writes_manual_lot_id and command[0] in (1, 2, 3, 4):
                defer_delete_lines += StockMoveLine.browse(command[1])
                if command[0] == 2:
                    explicit_delete_lines += StockMoveLine.browse(command[1])
            if command[0] in (0, 1) and 'manual_lot_id' in command[2]:
                writes_manual_lot_id = True
        if defer_delete_lines:
            original_context = self.env.context
            self = self.with_context(
                manual_lot_move_lines=dict(
                    (ml.id, ml.product_qty) for ml in defer_delete_lines)
                )
        result = super().write(vals)
        explicit_delete_lines.unlink()
        if defer_delete_lines:
            self = self.with_context(original_context)
            # Clean up any remaining zero qty move lines
            move_lines = self.env["stock.move.line"].search(
                [("id", "in", defer_delete_lines.ids), ("product_qty", "=", 0)])
            if move_lines:
                moves = move_lines.mapped("move_id")
                move_lines.unlink()
                moves._recompute_state()
                for picking in moves.mapped("picking_id").with_context():
                    try:
                        with self.env.cr.savepoint():
                            picking.action_assign()
                    except UserError:
                        pass
        return result
