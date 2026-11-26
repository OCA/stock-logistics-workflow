# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    def write(self, vals):
        res = super(
            StockWarehouse, self.with_context(restrict_location_defer_check=True)
        ).write(vals)
        self.env["stock.picking.type"].with_context(active_test=False).search(
            [
                ("warehouse_id", "in", (self | self.resupply_wh_ids).ids),
                ("restrict_location", "=", True),
            ]
        )._check_restrict_location()
        return res
