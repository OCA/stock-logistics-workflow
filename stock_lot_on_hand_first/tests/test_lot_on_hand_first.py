# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import TransactionCase
from odoo.tools import float_is_zero


class TestLotOnHandFirst(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_precision = cls.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        cls.product = cls.env.ref("stock.product_cable_management_box").copy()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.delivery_order_picking_type = cls.env.ref("stock.picking_type_out")

    @classmethod
    def _create_lot(cls, product, lot_name, qty=0):
        lot = cls.env["stock.lot"].create(
            {
                "name": lot_name,
                "product_id": product.id,
                "company_id": cls.env.company.id,
            }
        )
        if not float_is_zero(qty, precision_digits=cls.uom_precision):
            cls.env["stock.quant"]._update_available_quantity(
                product, cls.stock_location, qty, lot_id=lot
            )
        return lot

    def test_lot_on_hand_first(self):
        """Check lots without a qty are at the end of the list"""
        # Create a few lots with quantities
        lot_1 = self._create_lot(self.product, "LOT-000001", 0)
        lot_2 = self._create_lot(self.product, "LOT-000002", 1)
        lot_3 = self._create_lot(self.product, "LOT-000003", 2)
        lot_4 = self._create_lot(self.product, "LOT-000004", 0)
        lot_5 = self._create_lot(self.product, "LOT-000005", 1)

        name_get_res = (
            self.env["stock.lot"]
            .with_context(name_search_qty_on_hand_first=True)
            .name_search(args=[("product_id", "=", self.product.id)])
        )

        expected_res = [
            (lot_2.id, lot_2.name),
            (lot_3.id, lot_3.name),
            (lot_5.id, lot_5.name),
            (lot_1.id, lot_1.name),
            (lot_4.id, lot_4.name),
        ]
        self.assertEqual(name_get_res, expected_res)

    def test_lot_on_hand_first_no_qty(self):
        """Check name_get does not break if we do not have a lot with qty"""
        # Create a few lots with quantities
        lot_1 = self._create_lot(self.product, "LOT-000001", 0)
        lot_2 = self._create_lot(self.product, "LOT-000002", 0)
        lot_3 = self._create_lot(self.product, "LOT-000003", 0)

        name_get_res = (
            self.env["stock.lot"]
            .with_context(name_search_qty_on_hand_first=True)
            .name_search(args=[("product_id", "=", self.product.id)])
        )
        expected_res = [
            (lot_1.id, lot_1.name),
            (lot_2.id, lot_2.name),
            (lot_3.id, lot_3.name),
        ]
        self.assertEqual(name_get_res, expected_res)

    def test_compute_display_lots_on_hand_first(self):
        """Test computed stored field"""
        self.assertTrue(self.delivery_order_picking_type.use_existing_lots)
        # Set lots on hand=True is stored properly
        self.delivery_order_picking_type.display_lots_on_hand_first = True
        self.assertTrue(self.delivery_order_picking_type.display_lots_on_hand_first)
        self.assertTrue(self.delivery_order_picking_type.use_existing_lots)
        # Unmark use_existing_lots must unmark display_lots_on_hand_first
        self.delivery_order_picking_type.use_existing_lots = False
        self.assertFalse(self.delivery_order_picking_type.use_existing_lots)
        self.assertFalse(self.delivery_order_picking_type.display_lots_on_hand_first)
        # Mark use_existing_lots should not change display_lots_on_hand_first
        self.delivery_order_picking_type.use_existing_lots = True
        self.assertTrue(self.delivery_order_picking_type.use_existing_lots)
        self.assertFalse(self.delivery_order_picking_type.display_lots_on_hand_first)

    def test_lot_on_hand_first_with_limit(self):
        """Check lots without a qty are at the end of the list"""
        # Create a few lots with quantities
        lot_1 = self._create_lot(self.product, "LOT-000001", 0)
        lot_2 = self._create_lot(self.product, "LOT-000002", 0)
        lot_3 = self._create_lot(self.product, "LOT-000003", 0)
        lot_4 = self._create_lot(self.product, "LOT-000004", 0)
        lot_5 = self._create_lot(self.product, "LOT-000005", 0)
        lot_6 = self._create_lot(self.product, "LOT-000006", 0)
        self._create_lot(self.product, "LOT-000007", 0)
        self._create_lot(self.product, "LOT-000008", 0)
        lot_9 = self._create_lot(self.product, "LOT-000009", 5)
        lot_10 = self._create_lot(self.product, "LOT-000010", 5)

        name_get_res = (
            self.env["stock.lot"]
            .with_context(name_search_qty_on_hand_first=True)
            .name_search(args=[("product_id", "=", self.product.id)], limit=8)
        )
        expected_res = [
            (lot_9.id, lot_9.name),
            (lot_10.id, lot_10.name),
            (lot_1.id, lot_1.name),
            (lot_2.id, lot_2.name),
            (lot_3.id, lot_3.name),
            (lot_4.id, lot_4.name),
            (lot_5.id, lot_5.name),
            (lot_6.id, lot_6.name),
        ]
        self.assertEqual(name_get_res, expected_res)
