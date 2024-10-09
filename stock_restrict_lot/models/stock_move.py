from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import OrderedSet


class StockMove(models.Model):
    _inherit = "stock.move"

    # seems better to not copy this field except when a move is split, because a move
    # can be copied in multiple different occasions and could even be copied with a
    # different product...
    restrict_lot_id = fields.Many2one(
        "stock.lot", string="Restrict Lot", copy=False, index=True
    )

    def _prepare_procurement_values(self):
        vals = super()._prepare_procurement_values()
        vals["restrict_lot_id"] = self.restrict_lot_id.id
        return vals

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields.append("restrict_lot_id")
        return distinct_fields

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(
            quantity=quantity, reserved_quant=reserved_quant
        )
        if self.restrict_lot_id:
            if (
                "lot_id" in vals
                and vals["lot_id"] is not False
                and vals["lot_id"] != self.restrict_lot_id.id
            ):
                raise exceptions.UserError(
                    _(
                        "Inconsistencies between reserved quant and lot restriction on "
                        "stock move"
                    )
                )
            vals["lot_id"] = self.restrict_lot_id.id
        return vals

    def _get_available_quantity(
        self,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
        allow_negative=False,
    ):
        self.ensure_one()
        if not lot_id and self.restrict_lot_id:
            lot_id = self.restrict_lot_id
        return super()._get_available_quantity(
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
            allow_negative=allow_negative,
        )

    def _update_reserved_quantity(
        self,
        need,
        available_quantity,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        self.ensure_one()
        if self.restrict_lot_id:
            lot_id = self.restrict_lot_id
        return super()._update_reserved_quantity(
            need,
            available_quantity,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )

    def _split(self, qty, restrict_partner_id=False):
        vals_list = super()._split(qty, restrict_partner_id=restrict_partner_id)
        if vals_list and self.restrict_lot_id:
            vals_list[0]["restrict_lot_id"] = self.restrict_lot_id.id
        return vals_list

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        self._check_lot_consistent_with_restriction()
        return res

    def _check_lot_consistent_with_restriction(self):
        """
        Check that the lot set on move lines
        is the same as the restricted lot set on the move
        """
        for move in self:
            if not (move.restrict_lot_id and move.move_line_ids):
                continue
            move_line_lot = move.mapped("move_line_ids.lot_id")
            if move.restrict_lot_id != move_line_lot:
                raise UserError(
                    _(
                        "The lot(s) %(move_line_lot)s being moved is "
                        "inconsistent with the restriction on "
                        "lot %(move_restrict_lot)s set on the move",
                        move_line_lot=", ".join(move_line_lot.mapped("display_name")),
                        move_restrict_lot=move.restrict_lot_id.display_name,
                    )
                )

    # Same as _rollup_move_origs but also for "done" moves.
    def _rollup_not_cancelled_move_origs(self, seen=False):
        if not seen:
            seen = OrderedSet()
        for dst in self.move_orig_ids:
            if dst.id not in seen and dst.state != "cancel":
                seen.add(dst.id)
                dst._rollup_move_origs(seen)
        return seen

    def write(self, vals):
        if "restrict_lot_id" not in vals:
            return super().write(vals)
        else:
            restrict_lot_id = vals.pop("restrict_lot_id")
            restrict_lot = self.env["stock.lot"].browse(restrict_lot_id)
            chained_moves = OrderedSet(self.ids)
            self._rollup_move_dests(chained_moves)
            self._rollup_not_cancelled_move_origs(chained_moves)
            chained_moves = self.env["stock.move"].browse(chained_moves)
            if any(
                [
                    sm.state == "done" and sm.lot_ids and sm.lot_ids != restrict_lot
                    for sm in chained_moves
                ]
            ):
                raise ValidationError(
                    _(
                        "You can't modify the Lot/Serial number "
                        "because at least one move in the chain has "
                        "already been done with another Lot/Serial number."
                    )
                )
            for move in chained_moves:
                super(StockMove, move).write({"restrict_lot_id": restrict_lot_id})
        return super().write(vals)
