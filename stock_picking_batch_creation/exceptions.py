# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _
from odoo.api import Environment
from odoo.exceptions import UserError


class NoPickingCandidateError(UserError):
    def __init__(self, env: Environment):
        self.env = env
        super().__init__(self.env._("no candidate pickings to batch"))


class PickingCandidateNumberLineExceedError(UserError):
    def __init__(self, picking, max_line):
        self.env = picking.env
        self.picking = picking
        self.env = picking.env
        super().__init__(
            self.env._(
                "At least one picking candidate found %(name)s but with more line "
                "to process than the maximum number of line allowed in a batch "
                "picking. (%(max_line)s) vs (%(line)s)",
                name=self.picking.name,
                max_line=max_line,
                line=len(self.picking.move_line_ids),
            )
        )


class NoSuitableDeviceError(UserError):
    def __init__(self, pickings):
        self.pickings = pickings
        self.env = pickings.env
        message = _("No device found for batch picking.")
        if pickings:
            message += self.env._(
                " Pickings %(names)s do not match any device",
                names=", ".join(self.pickings.mapped("name")),
            )
        super().__init__(message)


class PickingSplitNotPossibleError(UserError):
    def __init__(self, picking):
        self.env = picking.env
        self.picking = picking
        super().__init__(
            self.env._("Picking %(name)s cannot be split", name=self.picking.name)
        )
