# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestStockLotLocation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location_1 = cls.env["stock.location"].create({"name": "Stock 1"})
        cls.location_2 = cls.env["stock.location"].create({"name": "Stock 2"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "is_storable": True,
            }
        )
        cls.lot = cls.env["stock.lot"].create(
            {"product_id": cls.product.id, "name": "LOT-001"}
        )

    def test_compute_location_ids(self):
        # Create quants with different locations
        quant_1 = self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "lot_id": self.lot.id,
                "location_id": self.location_1.id,
                "quantity": 10,
            }
        )
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "lot_id": self.lot.id,
                "location_id": self.location_2.id,
                "quantity": 5,
            }
        )

        self.lot._compute_location_ids()

        self.assertIn(
            self.location_1,
            self.lot.location_ids,
            "Location 1 should be in lot.location_ids",
        )
        self.assertIn(
            self.location_2,
            self.lot.location_ids,
            "Location 2 should be in lot.location_ids",
        )

        # Set one quant to zero and recompute
        quant_1.quantity = 0
        self.lot._compute_location_ids()

        self.assertNotIn(
            self.location_1,
            self.lot.location_ids,
            "Location 1 should not be in lot.location_ids after quantity is zero",
        )
        self.assertIn(
            self.location_2,
            self.lot.location_ids,
            "Location 2 should still be in lot.location_ids",
        )
