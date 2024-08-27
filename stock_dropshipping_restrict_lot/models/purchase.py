#   Copyright (c) 2024 Groupe Voltaire
#   @author Emilie SOUTIRAS  <emilie.soutiras@groupevoltaire.com>
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        for re in res:
            re["restrict_lot_id"] = self.sale_line_id.lot_id.id
        return res

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        res = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        res["lot_id"] = values.get("restrict_lot_id", False)
        return res
