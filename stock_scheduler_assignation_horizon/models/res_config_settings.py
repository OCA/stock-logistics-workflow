# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    stock_horizon_move_assignation = fields.Boolean(
        "Use Assignation Limit",
        config_parameter="stock_scheduler_assignation_horizon.stock_horizon_move_assignation",
        readonly=False,
        help="Enable scheduler assignation horizon limit for all companies",
    )
    stock_horizon_move_assignation_limit = fields.Integer(
        "Assignation Horizon",
        config_parameter="stock_scheduler_assignation_horizon."
        "stock_horizon_move_assignation_limit",
        readonly=False,
        help="Only reserve moves that are scheduled within the specified number of days",
    )

    @api.constrains("stock_horizon_move_assignation_limit")
    def _check_stock_horizon_move_assignation_limit(self):
        for record in self:
            if record.stock_horizon_move_assignation_limit < 0:
                raise ValidationError(_("The assignation horizon cannot be negative"))
