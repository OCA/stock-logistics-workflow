# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    is_moves_assignation_limited = fields.Boolean(
        "Scheduler Assignation Limit",
        related="company_id.is_moves_assignation_limited",
        readonly=False,
        help="Check this box to prevent the scheduler from "
        "assigning moves before the horizon below",
    )
    moves_assignation_horizon = fields.Integer(
        "Assignation Horizon",
        related="company_id.moves_assignation_horizon",
        readonly=False,
        help="Only reserve moves that are scheduled within the specified number of days",
    )

    @api.constrains("moves_assignation_horizon")
    def _check_moves_assignation_horizon(self):
        for record in self:
            if record.moves_assignation_horizon < 0:
                raise ValidationError(_("The assignation horizon cannot be negative"))
