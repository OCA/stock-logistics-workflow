# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


def is_lesser(value, other, rounding):
    return float_compare(value, other, precision_rounding=rounding) == -1


def is_bigger(value, other, rounding):
    return float_compare(value, other, precision_rounding=rounding) == 1


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _change_lot_free_other_lines(self, need, location, product, lot, package):
        self.ensure_one()
        to_reassign_moves = self.move_id.browse()
        freed_quantity = 0
        rounding = product.uom_id.rounding
        # We switch reservations with other move lines that have not
        # yet been processed
        other_lines = self.env["stock.move.line"].search(
            [
                ("lot_id", "=", lot.id),
                ("product_id", "=", product.id),
                ("location_id", "=", location.id),
                ("package_id", "=", package.id),
                ("state", "in", ("partially_available", "assigned")),
                ("reserved_uom_qty", ">", 0),
                ("qty_done", "=", 0),
            ],
            order="reserved_uom_qty desc",
        )
        # Favor lines from non-printed pickings.
        other_lines.sorted(
            lambda ml: (
                ml.picking_id == self.picking_id or not ml.picking_id.printed,
                -ml.reserved_uom_qty,
            )
        )
        # Stop when required quantity is reached
        for line in other_lines:
            freed_quantity += line.reserved_qty
            to_reassign_moves |= line.move_id
            # if we leave the package level, it will try to reserve the same
            # one again. This will trigger the deletion of the package level
            line.package_level_id.move_line_ids.result_package_id = False
            # unreserve qties of other lines
            line.unlink()
            if not is_lesser(freed_quantity, need, rounding):
                # We reached the required quantity
                break

        return (freed_quantity, to_reassign_moves)

    def write(self, vals):
        if self.env.context.get("bypass_reservation_update"):
            return super().write(vals)

        if not vals.get("lot_id"):
            return super().write(vals)

        res, already_processed, to_reassign_moves = self._do_change_lot(vals)
        res &= super(StockMoveLine, self - already_processed).write(vals)
        if to_reassign_moves:
            to_reassign_moves._action_assign()

        return res

    def _do_change_lot(self, vals):
        """
        Change the lot assigned to stock move lines, handling reservation logic.

        Attempts to change the lot of the current stock move lines to `vals["lot_id"]`.
        Ensures the new lot belongs to the same product, checks available quantities,
        and manages reservations. If not enough is available, tries to free up reserved
        quantities from other move lines. Updates the package if needed and partially
        reserves if full reservation is not possible.

        :param vals (dict): Values to update, must include "lot_id". May also include
            "location_id" and "package_id".

        :returns tuple:
            - res (bool): True if successful for all move lines.
            - already_processed (recordset): Move lines already processed.
            - to_reassign_moves (recordset): Moves needing reassignment.

        :raises UserError: If the new lot does not belong to the same product.
        """
        res = True
        already_processed = self.browse()
        to_reassign_moves = self.env["stock.move"]
        lot = self.env["stock.lot"].browse(vals["lot_id"])
        for move_line in self:
            if move_line.move_id._should_bypass_reservation(move_line.location_id):
                continue
            if not move_line.lot_id or move_line.lot_id == lot:
                continue

            product = move_line.product_id
            rounding = product.uom_id.rounding
            if lot.product_id != product:
                raise UserError(_("You cannot change to a lot of a different product"))

            location = move_line.location_id.browse(
                vals.get("location_id", move_line.location_id.id)
            )
            package = move_line.package_id.browse(
                vals.get("package_id", move_line.package_id.id)
            )

            available_quantity = 0
            # Collect new lot inside or outside a package (strict=False)
            quants = (
                self.env["stock.quant"]
                ._gather(
                    product,
                    location,
                    lot_id=lot,
                    package_id=package,
                    strict=False,
                )
                .filtered(
                    lambda q, r=rounding, loc=location: q.location_id == loc
                    and is_bigger(q.quantity, 0, r)
                )
            )
            if quants:
                quants_available = quants.filtered(
                    lambda q, r=rounding: is_bigger(
                        q.quantity - q.reserved_quantity, 0, r
                    )
                )

                if (
                    not package
                    and quants_available
                    and all(q.package_id for q in quants_available)
                ):
                    # all available quants are in a package, set one on the
                    # line to allow the reservation
                    package = quants_available.sorted(
                        lambda q: q.quantity - q.reserved_quantity, reverse=True
                    )[0].package_id
                    vals["package_id"] = package.id

                for quant in quants_available:
                    if package and quant.package_id != package:
                        continue
                    available_quantity += quant.quantity - quant.reserved_quantity

                if is_lesser(available_quantity, move_line.reserved_qty, rounding):
                    need = move_line.reserved_qty - available_quantity
                    (
                        freed_quantity,
                        to_reassign_moves,
                    ) = move_line._change_lot_free_other_lines(
                        need, location, product, lot, package
                    )
                    available_quantity += freed_quantity
                    to_reassign_moves |= to_reassign_moves

                    if is_lesser(
                        available_quantity, move_line.reserved_qty, rounding
                    ) and is_bigger(available_quantity, 0, rounding):
                        # When a partial quantity is found, find other
                        # available goods for the lines which were using
                        # the lot before...
                        to_reassign_moves |= self.move_id

            if is_lesser(available_quantity, move_line.reserved_qty, rounding):
                new_uom_qty = product.uom_id._compute_quantity(
                    available_quantity,
                    move_line.product_uom_id,
                    rounding_method="HALF-UP",
                )
                values = vals.copy()
                values["reserved_uom_qty"] = new_uom_qty
                res &= super(StockMoveLine, move_line).write(values)
                # recompute the state to be "partially_available"
                move_line.move_id._recompute_state()
                already_processed |= move_line
        return res, already_processed, to_reassign_moves
