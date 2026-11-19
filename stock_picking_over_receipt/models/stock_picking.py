# Copyright 2026 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from markupsafe import Markup

from odoo import models
from odoo.exceptions import UserError
from odoo.tools import formatLang


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_split_transfer(self):
        # OVERWRITE for a receipt with a line received above its demand: core
        # raises on such a line before doing anything, and has no hook to skip
        # that check. Any other transfer goes to core.
        if any(p.picking_type_code != "incoming" for p in self) or not any(
            m.product_uom.compare(m.quantity, m.product_uom_qty) > 0
            for m in self.move_ids
        ):
            return super().action_split_transfer()
        # Copy of core's method from here, with the changes marked REMOVED and
        # CHANGED.
        # REMOVED: "Nothing to split" when no line has a quantity, as a line
        # above its demand has one.
        # CHANGED: `>= 0` instead of `== 0`, so a line above its demand counts
        # as done too. Otherwise, with every line done or above, nothing is
        # split and `_create_backorder()` gets no moves, so it moves them all.
        if all(
            m.product_uom.compare(m.quantity, m.product_uom_qty) >= 0
            for m in self.move_ids
        ):
            raise UserError(
                self.env._(
                    "%s: Nothing to split, all demand is done. For split you need "
                    "at least one line not fully fulfilled",
                    self.display_name,
                )
            )
        # REMOVED: "Can't split: quantities done can't be above demand". Such a
        # line is not split by `stock.move._create_backorder()`: it stays whole
        # on this picking with the received quantity.
        moves = self.move_ids.filtered(
            lambda m: m.state not in ("done", "cancel") and m.quantity != 0
        )
        backorder_moves = moves._create_backorder()
        backorder_moves += self.move_ids.filtered(lambda m: m.quantity == 0)
        self._create_backorder(backorder_moves=backorder_moves)

    def _action_done(self):
        # OVERRIDE: tell the responsible about lines received above demand.
        res = super()._action_done()
        for picking in self.filtered(lambda p: p.picking_type_code == "incoming"):
            over_moves = picking.move_ids.filtered(
                lambda m: (
                    m.state == "done"
                    and m.product_uom.compare(m.quantity, m.product_uom_qty) > 0
                )
            )
            if not over_moves:
                continue
            picking.activity_schedule(
                "mail.mail_activity_data_todo",
                # A backorder is created by whoever split it off, possibly a
                # cron (e.g. an integration): use the receipt's creator.
                user_id=(
                    picking.user_id or (picking.backorder_id or picking).create_uid
                ).id,
                summary=self.env._("Received above demand"),
                note=Markup("<ul>%s</ul>")
                % Markup().join(
                    Markup("<li>%s: %s / %s %s</li>")
                    % (
                        move.product_id.display_name,
                        formatLang(self.env, move.quantity, dp="Product Unit"),
                        formatLang(self.env, move.product_uom_qty, dp="Product Unit"),
                        move.product_uom.name,
                    )
                    for move in over_moves
                ),
            )
        return res
