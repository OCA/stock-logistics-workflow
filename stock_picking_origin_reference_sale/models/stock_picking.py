# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models

SO_MODEL_NAME = "sale.order"


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _selection_origin_reference(self):
        return super()._selection_origin_reference() + [(SO_MODEL_NAME, "Sales Order")]

    @api.depends(lambda x: x._get_depends_compute_origin_reference())
    def _compute_origin_reference(self):
        res = super()._compute_origin_reference()
        for picking in self:
            if not picking.origin_reference:
                rel_sale = self.env[SO_MODEL_NAME].search(
                    [("name", "=", picking.origin)], limit=1
                )
                if rel_sale:
                    picking.origin_reference = f"{SO_MODEL_NAME},{rel_sale.id}"
        return res
