# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author Vincent Van Rossem <vincent.vanrossem@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, vals):
        # Override the write method to propagate the date to the destination moves.
        if "date" not in vals or self.env.context.get("_propagate_date_no_recursion"):
            return super().write(vals)
        dates = {d["id"]: d["date"] for d in self.read(["date"], load=None)}
        res = super().write(vals)
        self._propagate_date_no_recursion(dates, vals["date"])
        return res

    def _get_moves_in_down_chain(self):
        """Get all the destination moves in the down chain of a moves recordset recursively."""
        if not self:
            return {}
        query = """
            WITH RECURSIVE chained_moves AS (
                SELECT
                    r.move_orig_id, r.move_orig_id as from_id, r.move_dest_id as dest_id
                FROM
                    stock_move_move_rel r
                WHERE r.move_orig_id IN %s

                UNION ALL

                SELECT
                    cm.move_orig_id,
                    r.move_orig_id AS from_id,
                    r.move_dest_id AS dest_id
                FROM
                    stock_move_move_rel r
                JOIN
                    chained_moves cm ON r.move_orig_id = cm.dest_id
                WHERE
                    r.move_dest_id != cm.move_orig_id
            )

            SELECT
                move_orig_id,
                array_agg(dest_id)
            FROM chained_moves
            GROUP BY move_orig_id;
        """

        self.env.cr.execute(query, (tuple(self.ids),))
        # key: original move, values: list of destination moves
        return dict(self.env.cr.fetchall())

    def _propagate_date_no_recursion(self, previous_dates, new_date):
        """Propagate the date of a move to its destination avoiding recursion."""
        if not self:
            return
        chained_dest_moves = self._get_moves_in_down_chain()
        if chained_dest_moves:
            for move in self:
                dest_move_ids = chained_dest_moves.get(move.id)
                if not dest_move_ids:
                    continue
                prev_date = previous_dates.get(move.id)
                if not prev_date:
                    continue
                delta = prev_date - fields.Datetime.to_datetime(new_date)
                dest_moves = self.browse(set(dest_move_ids))
                for dest_move in dest_moves.with_context(
                    _propagate_date_no_recursion=1
                ):
                    if dest_move.state not in ("done", "cancel"):
                        dest_move.date = dest_move.date - delta
