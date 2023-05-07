# Copyright 2021 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _get_moves_to_assign_domain(self, company_id):
        moves_domain = super()._get_moves_to_assign_domain(company_id)
        moves_domain = expression.AND(
            [[("reservation_date", "<=", fields.Date.today())], moves_domain]
        )
        return moves_domain
