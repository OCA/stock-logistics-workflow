# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError


class SplitPickNotAllowedInStateError(UserError):
    """
    Exception class to represent stock picking split error for picking wrong state
    """

    def __init__(self, env, picking):
        self.env = env
        super().__init__(
            _(
                "Cannot split picking %(name)s in state %(state)s",
                name=picking.name,
                state=picking.state,
            )
        )


class NotPossibleToSplitPickError(UserError):
    """
    Exception class to represent stock picking split error for picking
    """

    def __init__(self, env, picking):
        self.env = env
        super().__init__(
            _("Cannot split off all moves from picking %(name)s", name=picking.name)
        )
