# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError


class NoPickingCandidateError(UserError):
    def __init__(self):
        super(NoPickingCandidateError, self).__init__(
            _("no candidate pickings to batch")
        )


class NoSuitableDeviceError(UserError):
    def __init__(self, pickings):
        self.pickings = pickings
        message = _("No device found for batch picking.")
        if pickings:
            message += _(
                " Pickings %(names)s do not match any device",
                names=", ".join(self.pickings.mapped("name")),
            )
        super(NoSuitableDeviceError, self).__init__(message)
