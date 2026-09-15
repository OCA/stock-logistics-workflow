# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    lead_time_profile_warehouse_factor = fields.Float(
        related="company_id.lead_time_profile_warehouse_factor", readonly=False
    )
    lead_time_profile_country_factor = fields.Float(
        related="company_id.lead_time_profile_country_factor", readonly=False
    )
    lead_time_profile_state_factor = fields.Float(
        related="company_id.lead_time_profile_state_factor", readonly=False
    )
    lead_time_profile_partner_factor = fields.Float(
        related="company_id.lead_time_profile_partner_factor", readonly=False
    )

    def open_lead_time_profile_list(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Lead Time Profiles",
            "res_model": "lead.time.profile",
            "view_mode": "tree",
        }
