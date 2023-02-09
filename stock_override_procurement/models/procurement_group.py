# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProcurementGroup(models.Model):

    _inherit = "procurement.group"

    @api.model
    def run(self, procurements, raise_user_error=True):
        procurements = self._override_procurements(procurements)
        return super().run(procurements, raise_user_error=raise_user_error)

    @api.model
    def _override_procurements(self, procurements):
        return [
            self._get_override_procurement(procurement) for procurement in procurements
        ]

    @api.model
    def _get_override_procurement(self, procurement):
        values = procurement.values

        def _get_override_value(field_name):
            return (
                values.get(field_name)
                if field_name in values
                else getattr(procurement, field_name)
            )

        return self.Procurement(
            product_id=_get_override_value("product_id"),
            product_qty=_get_override_value("product_qty"),
            product_uom=_get_override_value("product_uom"),
            location_id=_get_override_value("location_id"),
            name=_get_override_value("name"),
            origin=_get_override_value("origin"),
            company_id=procurement.company_id,
            values=procurement.values,
        )
