# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestStockValuationLayerVendor(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "is_storable": True, "standard_price": 100.0}
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

    def _create_purchase_order(self, partner):
        return self.env["purchase.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "product_qty": 10.0,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )

    def _receive_purchase_order(self, purchase_order):
        """Confirm the order and validate its receipt, as a user would."""
        purchase_order.button_confirm()
        picking = purchase_order.picking_ids
        picking.action_assign()
        picking.move_ids.write({"quantity": 10.0, "picked": True})
        picking._action_done()
        return picking

    def test_vendor_id_set_from_purchase_move(self):
        picking = self._receive_purchase_order(self._create_purchase_order(self.vendor))
        svl = picking.move_ids.stock_valuation_layer_ids
        self.assertTrue(svl)
        self.assertEqual(svl.vendor_id, self.vendor)

    def test_vendor_id_set_from_purchase_move_batch(self):
        vendor_2 = self.env["res.partner"].create({"name": "Test Vendor 2"})
        picking_1 = self._receive_purchase_order(
            self._create_purchase_order(self.vendor)
        )
        picking_2 = self._receive_purchase_order(self._create_purchase_order(vendor_2))
        self.assertEqual(
            picking_1.move_ids.stock_valuation_layer_ids.vendor_id, self.vendor
        )
        self.assertEqual(
            picking_2.move_ids.stock_valuation_layer_ids.vendor_id, vendor_2
        )

    def test_vendor_id_empty_without_purchase(self):
        # Receiving stock without a purchase order (here via an inventory
        # adjustment) produces a layer whose move has no purchase line.
        quant = self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.stock_location.id,
                "inventory_quantity": 10.0,
            }
        )
        quant.action_apply_inventory()
        svl = self.env["stock.valuation.layer"].search(
            [("product_id", "=", self.product.id)]
        )
        self.assertTrue(svl)
        self.assertFalse(svl.vendor_id)

    def test_vendor_id_empty_without_move(self):
        # A layer with no stock move (e.g. a manual revaluation) must not raise
        # and must have no vendor. This path has no realistic document flow, so
        # the layer is created directly.
        svl = self.env["stock.valuation.layer"].create(
            {
                "product_id": self.product.id,
                "company_id": self.env.company.id,
                "quantity": 10.0,
                "value": 1000.0,
                "unit_cost": 100.0,
            }
        )
        self.assertFalse(svl.vendor_id)
