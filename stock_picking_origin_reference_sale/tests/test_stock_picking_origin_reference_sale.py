# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.addons.stock_picking_origin_reference.tests import (
    test_stock_picking_origin_reference,
)


class TestStockPickingOriginReferenceSale(
    test_stock_picking_origin_reference.TestStockPickingOriginReference
):
    def setUp(self):
        super().setUp()
        self.sale_model = self.env["sale.order"]

    def _create_sale(self, partner, product):
        sale = self.sale_model.create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": 5,
                            "price_unit": 500,
                        },
                    )
                ],
            }
        )
        return sale

    def test_01_check_correct_value(self):
        """
        Check that the Transfer created from the SO is referencing it.
        """
        sale = self._create_sale(self.partner, self.product)
        sale.action_confirm()
        self.assertTrue(sale.picking_ids)
        self.assertEqual(
            len(sale.picking_ids), 1, "Only one Transfer should be created."
        )
        picking = sale.picking_ids
        self.assertEqual(
            picking.origin_reference, sale, "The Transfer should reference the SO."
        )
