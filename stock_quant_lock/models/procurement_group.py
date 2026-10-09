# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _get_rule(self, product_id, location_id, values):
        quant = values.get("quant_lock_quant_id")
        if quant:
            # Never fall back on the product or warehouse routes: a quant lock
            # must be done by the lock rule of the requested route.
            return quant._get_lock_rule(values["route_ids"])
        return super()._get_rule(product_id, location_id, values)
