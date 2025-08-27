# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from collections import OrderedDict

from odoo import models

MOVE_STATES_IN_PROGRESS = ("confirmed", "waiting", "partially_available", "assigned")


class StockMove(models.Model):
    _inherit = "stock.move"

    def sync_checkout_destination(self, location):
        moves = self.filtered(lambda m: m.state != "done")
        if not moves:
            return
        # Normally the move destination does not change. But when using other
        # addons, such as stock_dynamic_routing, the source location of the
        # destination move can change, so handle this case too. (there is a
        # glue module stock_dynamic_routing_checkout_sync).
        moves_to_update = self.filtered(lambda m: m.location_dest_id != location)
        moves_to_update.picking_id.location_dest_id = location
        moves_to_update.location_dest_id = location
        # Sync the source of the destination move too, if it's still waiting.
        moves_dest = moves_to_update.move_dest_ids.filtered(
            # FIXME add partially_available?
            lambda m: m.state in MOVE_STATES_IN_PROGRESS and m.location_id != location
        )
        moves_dest.picking_id.location_id = location
        moves_dest.location_id = location

        lines = moves.mapped("move_line_ids").filtered(
            lambda line: line.location_dest_id != location and line.state != "done"
        )
        lines.write({"location_dest_id": location.id})
        lines.package_level_id.write({"location_dest_id": location.id})

    def _moves_to_sync_checkout(self):
        selected_pickings = OrderedDict()
        for move in self:
            # Excluding picking types is used to sync the moves one picking
            # type at a time from the wizard.
            dest_pickings = move.mapped("move_dest_ids.picking_id").filtered(
                lambda pick: pick.picking_type_id.checkout_sync
            )
            if not dest_pickings:
                continue

            moves = (move | move.common_dest_move_ids).filtered(
                lambda move: move.state not in ("done", "cancel")
            )
            for dest_picking in dest_pickings:
                selected_pickings.setdefault(dest_picking, set())
                selected_pickings[dest_picking] |= set(moves.ids)
        return {
            picking: self.env["stock.move"].browse(move_ids)
            for picking, move_ids in selected_pickings.items()
        }
