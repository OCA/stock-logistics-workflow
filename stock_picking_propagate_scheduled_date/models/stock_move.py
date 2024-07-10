# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author Vincent Van Rossem <vincent.vanrossem@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _propagate_date(self, new_date):
        """Propagate the date of a move to its destination."""
        # This should never happen (see :meth:`_register_hook`), but still..
        if "date_propagation_ids" not in self.env.context:
            self = self.with_context(date_propagation_ids=set())
        # Update the already propagated ids, to avoid impacting the same move twice
        already_propagated_ids = self.env.context.get("date_propagation_ids")
        already_propagated_ids.update(self.ids)  # keep the same variable reference
        # Propagate the date delta to destination moves
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
        return super(StockMove, self).write(vals)

    def _register_hook(self):
        # Patch `write` to initialize `date_propagated_ids` in the context, so that
        # it's available on the whole stack chain, independent of the MRO.
        res = super()._register_hook()

        def make_write():
            def write(self, vals, **kw):
                if "date_propagation_ids" not in self.env.context:
                    self = self.with_context(date_propagation_ids=set())
                return write.origin(self, vals, **kw)

            return write

        self._patch_method("write", make_write())
        return res
