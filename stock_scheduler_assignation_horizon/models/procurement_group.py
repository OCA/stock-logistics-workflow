# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

import pytz

from odoo import models
from odoo.osv import expression


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    def _get_moves_to_assign_domain(self, company_id):
        domain = super()._get_moves_to_assign_domain(company_id)
        company = self.env["res.company"].browse(company_id)
        if company.is_moves_assignation_limited:
            domain = self._get_moves_to_assign_domain_assignation_limited(
                domain, company
            )
        return domain

    def _get_moves_to_assign_domain_assignation_limited(self, domain, company):
        company_tz = pytz.timezone(company.partner_id.tz or "UTC")
        max_date = (
            datetime.combine(
                datetime.now(company_tz)
                + timedelta(days=company.moves_assignation_horizon),
                datetime.max.time(),
            )
            .astimezone(pytz.utc)
            .replace(tzinfo=None)
        )
        return expression.AND(
            [
                domain,
                [("date", "<=", max_date)],
            ]
        )
