# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields

from odoo.addons.stock_picking_origin_reference.tests import (
    test_stock_picking_origin_reference,
)


class TestStockPickingOriginReferencePurchase(
    test_stock_picking_origin_reference.TestStockPickingOriginReference
):
    def setUp(self):
        super().setUp()
        self.purchase_model = self.env["purchase.order"]

    def _create_purchase(self, partner, product):
        purchase = self.purchase_model.create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_qty": 5,
                            "product_uom": product.uom_id.id,
                            "price_unit": 500,
                            "date_planned": fields.datetime.now(),
                        },
                    )
                ],
            }
        )
        return purchase

    def test_01_check_correct_value(self):
        """
        Check that the Transfer created from the purchase is referencing it.
        """
        purchase = self._create_purchase(self.partner, self.product)
        purchase.button_confirm()
        self.assertTrue(purchase.picking_ids)
        self.assertEqual(
            len(purchase.picking_ids), 1, "Only one Transfer should be created."
        )
        picking = purchase.picking_ids
        self.assertEqual(
            picking.origin_reference, purchase, "The Transfer should reference the PO."
        )
