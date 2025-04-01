# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    lead_time_profile_warehouse_factor = fields.Float(default=1.0)
    lead_time_profile_country_factor = fields.Float(default=1.0)
    lead_time_profile_state_factor = fields.Float(default=1.0)
    lead_time_profile_partner_factor = fields.Float(default=1.0)
