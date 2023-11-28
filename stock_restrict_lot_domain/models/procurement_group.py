# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.tools.safe_eval import safe_eval


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, procurements, raise_user_error=True):
        for procurement in procurements:
            if "restrict_lot_id" in procurement.values:
                product_domain = safe_eval(
                    procurement.company_id.product_apply_lot_restriction_domain
                )
                if not procurement.product_id.filtered_domain(product_domain):
                    del procurement.values["restrict_lot_id"]
        return super().run(procurements, raise_user_error)
