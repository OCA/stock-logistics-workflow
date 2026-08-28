# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import Basecommon


class TestStockScrapCancel(Basecommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "is_storable": True}
        )
        warehouse = cls.env.ref("stock.warehouse0")
        cls.location = warehouse.lot_stock_id
        cls.scrap = cls.env["stock.scrap"].create(
            {
                "product_id": cls.product.id,
                "scrap_qty": 1.00,
                "product_uom_id": cls.product.uom_id.id,
                "location_id": cls.location.id,
            }
        )

    def _update_qty_on_hand_product(self, new_qty):
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.location, new_qty
        )
        self.product.invalidate_recordset(["qty_available"])

    def test_stock_scrap_process(self):
        self.assertEqual(self.product.qty_available, 0)
        self._update_qty_on_hand_product(self.scrap.scrap_qty)
        self.assertEqual(self.product.qty_available, 1)
        self.scrap.action_validate()
        self.assertEqual(self.product.qty_available, 0)
        self.assertEqual(self.scrap.state, "done")
        self.scrap.action_cancel()
        self.assertEqual(self.product.qty_available, 1)
        self.assertEqual(self.scrap.state, "cancel")
        self.assertEqual(self.scrap.scrap_qty, 1)
        self.assertFalse(self.scrap.move_ids)
        self.scrap.action_draft()
        self.assertEqual(self.scrap.state, "draft")
