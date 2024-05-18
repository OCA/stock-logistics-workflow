# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author Vincent Van Rossem <vincent.vanrossem@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _propagate_date(self, new_date):
        """Propagate the date of a move to its destination."""
        already_propagated_ids = self.env.context.get(
            "date_propagation_ids", set()
        ) | set(self.ids)
        self = self.with_context(date_propagation_ids=already_propagated_ids)
        for move in self:
            if move.date:
                delta = move.date - fields.Datetime.to_datetime(new_date)
            else:
                delta = 0
            for move_dest in move.move_dest_ids:
                if move_dest.state in ("done", "cancel"):
                    continue
                if move_dest.id in already_propagated_ids:
                    continue
                move_dest.date -= delta

    def write(self, vals):
        # propagate date changes in the stock move chain
        if "date" in vals:
            self._propagate_date(vals.get("date"))
        return super().write(vals)
