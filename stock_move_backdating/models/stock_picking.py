# Copyright 2018 Alex Comba - Agile Business Group
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    date_backdating = fields.Datetime(
        string="Forced Effective Date",
        help="The Actual Movement Date of the Operations "
        "only if they have all the same value.",
        compute="_compute_date_backdating",
        store=True,
    )

    @api.depends("move_line_ids.date_backdating")
    def _compute_date_backdating(self):
        for picking in self:
            move_lines = picking.move_line_ids
            move_lines_back_dates = move_lines.mapped("date_backdating")
            move_lines_back_date = set(move_lines_back_dates)
            if len(move_lines_back_date) == 1:
                date_backdating = move_lines_back_date.pop()
            else:
                date_backdating = False
            picking.date_backdating = date_backdating

    def _backdating_update_picking_date(self):
        """Set date_done as the youngest date among the done moves."""
        self.ensure_one()
        moves = self.move_ids
        done_moves = moves.filtered(lambda m: m.state == "done")
        dates = done_moves.mapped("date")
        if dates:
            self.date_done = max(dates)
        return True

    def _action_done(self):
        # Capture per-move backdating dates BEFORE super, since move_lines
        # may be recreated/unlinked during _action_done (losing date_backdating).
        move_backdating = {}
        for picking in self:
            for move in picking.move_ids:
                line = move.move_line_ids[:1]
                if line.date_backdating:
                    move_backdating[move.id] = line.date_backdating

        result = super()._action_done()

        # After all super processing is complete, force the backdated date on
        # the moves and their move_lines. This runs at picking level so it
        # happens once the move-level _action_done, account move creation,
        # and picking write of date_done are already done.
        if move_backdating:
            # Flush any pending ORM writes (notably move.date = now() set by
            # stock._action_done) BEFORE our SQL UPDATE; otherwise a later
            # flush would overwrite our backdated value.
            self.env.flush_all()
            for move_id, date_backdating in move_backdating.items():
                self.env.cr.execute(
                    "UPDATE stock_move SET date = %s WHERE id = %s",
                    (date_backdating, move_id),
                )
                self.env.cr.execute(
                    "UPDATE stock_move_line "
                    "SET date = %s, date_backdating = %s "
                    "WHERE move_id = %s",
                    (date_backdating, date_backdating, move_id),
                )
            # Drop the cache without flushing again (we just flushed and the
            # SQL UPDATE bypasses the ORM, so the cache is now stale).
            self.env.invalidate_all(flush=False)

        pickings_backdate = self.filtered_domain(
            [
                "|",
                ("date_backdating", "!=", False),
                ("move_ids.move_line_ids.date_backdating", "!=", False),
            ]
        )
        for picking in pickings_backdate:
            picking._backdating_update_picking_date()
        return result
