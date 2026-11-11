# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _get_procurements_to_merge_groupby(self, procurement):
        """Do not group purchase order line if they are linked to different
        vendor comment in sale order line.
        """
        return (
            procurement.values.get("vendor_id"),
            procurement.values.get("vendor_comment"),
            *super()._get_procurements_to_merge_groupby(procurement),
        )

    def _get_custom_move_fields(self):
        fields = super()._get_custom_move_fields()
        fields.extend(["vendor_id", "vendor_comment"])
        return fields
