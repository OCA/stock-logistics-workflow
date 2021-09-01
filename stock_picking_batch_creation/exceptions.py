# -*- coding: utf-8 -*-
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
        super(NoSuitableDeviceError, self).__init__(
            _("no device found for batch picking. Pickings %s do not match any device")
            % self.pickings.mapped("name")
        )
