# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo import api, models


# Copy of Model._patch_method + Model._revert_method of Odoo 16.0 removed in Odoo 17.0
def patch_method(cls, name, method):
    origin = getattr(cls, name)
    method.origin = origin
    # propagate decorators from origin to method, and apply api decorator
    wrapped = api.propagate(origin, method)
    setattr(cls, name, wrapped)


def revert_method(cls, name):
    method = getattr(cls, name)
    origin = method.origin
    setattr(cls, name, origin)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @contextmanager
    def _get_move_free_reservation_ids(self):
        """A context manager method to collect the move where the reservation has
        been freed

        It will wrap the `_free_reservation` method of the `stock.move.line` model.
        to collect the move impacted by the reservation removal.
        """
        move_to_reassign_ids = set()

        def _free_reservation(*args, **kwargs):
            with args[0]._get_move_recomputed_state_ids() as move_recomputed_state_ids:
                res = _free_reservation.origin(*args, **kwargs)
                move_to_reassign_ids.update(move_recomputed_state_ids)
                return res

        try:
            patch_method(
                type(self.env["stock.move.line"]),
                "_free_reservation",
                _free_reservation,
            )
            yield move_to_reassign_ids
        finally:
            revert_method(type(self.env["stock.move.line"]), "_free_reservation")

    @contextmanager
    def _get_move_recomputed_state_ids(self):
        """A context manager method to collect the move where the state has been
        recomputed

        It will wrap the `_recompute_state` method of the `stock.move` model.
        to collect the move impacted by the reservation removal.
        """
        # define an object that will be used to collect the move ids
        move_to_reassign_ids = set()

        def _recompute_state(self):
            move_to_reassign_ids.update(self.ids)
            _recompute_state.origin(self)

        try:
            patch_method(
                type(self.env["stock.move"]), "_recompute_state", _recompute_state
            )
            yield move_to_reassign_ids
        finally:
            revert_method(type(self.env["stock.move"]), "_recompute_state")
