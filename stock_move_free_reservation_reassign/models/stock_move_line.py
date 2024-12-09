# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo import models


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    @contextmanager
    def _get_move_free_reservation_ids(self):
        """A context manager method to collect the move where the reservation has
        been freed

        It will wrap the `_free_reservation` method of the `stock.move.line` model.
        to collect the move impacted by the reservation removal.
        """
        wrapped = self.env["stock.move.line"].__class__._free_reservation
        move_to_reassign_ids = set()

        def _free_reservation(*args, **kwargs):
            with args[0]._get_move_recomputed_state_ids() as move_recomputed_state_ids:
                res = wrapped(*args, **kwargs)
                move_to_reassign_ids.update(move_recomputed_state_ids)
                return res

        try:
            self.env["stock.move.line"]._patch_method(
                "_free_reservation", _free_reservation
            )
            yield move_to_reassign_ids
        finally:
            self.env["stock.move.line"]._revert_method("_free_reservation")

    @contextmanager
    def _get_move_recomputed_state_ids(self):
        """A context manager method to collect the move where the state has been
        recomputed

        It will wrap the `_recompute_state` method of the `stock.move` model.
        to collect the move impacted by the reservation removal.
        """
        wrapped = self.env["stock.move"].__class__._recompute_state
        # define an object that will be used to collect the move ids
        move_to_reassign_ids = set()

        def _recompute_state(self):
            move_to_reassign_ids.update(self.ids)
            wrapped(self)

        try:
            self.env["stock.move"]._patch_method("_recompute_state", _recompute_state)
            yield move_to_reassign_ids
        finally:
            self.env["stock.move"]._revert_method("_recompute_state")
