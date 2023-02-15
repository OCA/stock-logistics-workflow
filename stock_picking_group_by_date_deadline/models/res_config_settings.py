# Copyright 2023 Foodles (http://www.foodles.co).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    deadline_date_rounding_threshold = fields.Float(
        string="Deadline date rounding threshold (hours)",
        config_parameter=(
            "stock_picking_group_by_date_deadline.deadline_date_rounding_threshold"
        ),
        default=24,
        help="Number of hours used to round down deadline date time on stock move. "
        "This gives a chance to merge moves or picking with the same deadline. "
        "(ie: if set to 6 hours, and deadline is 17:22:35 then deadline "
        "will be force to 12:00:00) "
        "Default is 24 hours for once a day",
    )
