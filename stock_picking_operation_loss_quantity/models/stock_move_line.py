# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    is_action_lose_quantity_allowed = fields.Boolean(
        compute="_compute_is_action_lose_quantity_allowed"
    )

    @api.depends("reserved_qty", "qty_done", "picking_id.picking_type_code")
    def _compute_is_action_lose_quantity_allowed(self):
        for rec in self:
            rec.is_action_lose_quantity_allowed = (
                rec.location_id.warehouse_id.use_loss_picking
                and (rec.qty_done - rec.reserved_qty < 0)
                and rec.state not in ("done", "draft")
                and rec.picking_id.picking_type_code != "incoming"
                and rec.picking_id.picking_type_id
                != rec.location_id.warehouse_id.loss_type_id
            )

    def action_lose_quantity(self):
        if any(not rec.is_action_lose_quantity_allowed for rec in self):
            raise UserError(_("You are not allowed to declare loss quantities"))
        return self._lose_quantity()

    def _unreserve_unprocessed_qty(self) -> float:
        self.ensure_one()
        unprocessed_qty = self.reserved_uom_qty - self.qty_done
        # Free the quantity that the operator was not able to process
        self.reserved_uom_qty = self.qty_done
        return unprocessed_qty

    def _reservation_is_updatable(self, quantity, reserved_quant):
        self.ensure_one()
        if self.env.context.get(
            "loss_quantity_prevent_reservation_update_on_done_lines"
        ) and not float_is_zero(
            self.qty_done, precision_rounding=self.product_uom_id.rounding
        ):
            # The operator already processed (fully or partially) this
            # operation: any quantity re-reserved for the same
            # product/location/lot/package/owner must land on a new move
            # line rather than silently topping up one the operator
            # already considers closed.
            return False
        return super()._reservation_is_updatable(quantity, reserved_quant)

    def _lose_quantity(self):
        """
        Main method used to declare a loss.

        It performs the following steps:
        1. Gather the quants related to the move line.
        2. Unreserve the quantity for the unprocessed part of the move line.
           If nothing was ever done on the line, it is left empty for now
           (see step 4).
        3. Lock the quants for the remaining available quantity using the
           warehouse's loss picking type.
        4. Re-reserve the move for the remaining quantity. Thanks to
           `_reservation_is_updatable`, this never updates a move line
           already processed by the operator: it creates a new move line
           instead. When this actually creates a new line for the move, the
           empty line(s) left by step 2 are dropped, as they are now
           redundant. If no new line is created (nothing else was available,
           or the freed quantity was merged into another not-yet-processed
           line), the empty line is kept as a visible placeholder.
        """
        empty_lines_by_move = defaultdict(lambda: self.browse())
        unprocessed_by_move = defaultdict(float)
        for line in self:
            if not line.is_action_lose_quantity_allowed:
                continue
            # strict is required when editing a line to match the exact quants
            # related to this move line.
            quants = self.env["stock.quant"]._gather(
                product_id=line.product_id,
                location_id=line.location_id,
                lot_id=line.lot_id,
                package_id=line.package_id,
                owner_id=line.owner_id,
            )
            quants._lock_quants_for_loss()
            unprocessed_by_move[line.move_id] += line._unreserve_unprocessed_qty()
            quants._lock_with_picking_type(line.location_id.warehouse_id.loss_type_id)
            if float_is_zero(
                line.reserved_uom_qty, precision_rounding=line.product_uom_id.rounding
            ):
                empty_lines_by_move[line.move_id] |= line

        for move, unprocessed_qty in unprocessed_by_move.items():
            if float_is_zero(
                unprocessed_qty, precision_rounding=move.product_uom.rounding
            ):
                continue
            # Unreserving a move line does not demote the move's state on its
            # own (Odoo only does this from write()/unlink() on the whole
            # move line recordset being processed together): force it so
            # `_action_assign` below does not skip a move it still considers
            # fully `assigned`.
            move._recompute_state()
            existing_line_ids = set(move.move_line_ids.ids)
            move.with_context(
                loss_quantity_prevent_reservation_update_on_done_lines=True
            )._action_assign()
            new_line_created = bool(set(move.move_line_ids.ids) - existing_line_ids)
            if new_line_created:
                empty_lines_by_move[move].unlink()
