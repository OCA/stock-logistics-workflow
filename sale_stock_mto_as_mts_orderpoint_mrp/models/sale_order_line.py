# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _get_procurement_wiz_for_orderpoint_ids(self, context):
        context.update({"ignore_bom_find": True})
        return super()._get_procurement_wiz_for_orderpoint_ids(context)
