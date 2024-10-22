# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models

PO_MODEL_NAME = "purchase.order"


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _selection_origin_reference(self):
        return super()._selection_origin_reference() + [
            (PO_MODEL_NAME, "Purchase Order")
        ]

    @api.depends(lambda x: x._get_depends_compute_origin_reference())
    def _compute_origin_reference(self):
        res = super()._compute_origin_reference()
        for picking in self:
            if not picking.origin_reference:
                rel_purchase = self.env[PO_MODEL_NAME].search(
                    [("name", "=", picking.origin)], limit=1
                )
                if rel_purchase:
                    picking.origin_reference = f"{PO_MODEL_NAME},{rel_purchase.id}"
        return res
