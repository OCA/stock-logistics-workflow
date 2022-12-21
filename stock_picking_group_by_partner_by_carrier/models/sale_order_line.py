# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020-2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_group_vals(self):
        vals = super()._prepare_procurement_group_vals()
        if not vals.get("sale_ids") and vals.get("sale_id"):
            vals["sale_ids"] = [(6, 0, [vals["sale_id"]])]
        return vals
