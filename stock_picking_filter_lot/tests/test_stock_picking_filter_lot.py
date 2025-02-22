# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase


class TestStockPickingFilterLot(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test product #1", "type": "product", "tracking": "lot"}
        )
        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "Test warehouse #1", "code": "TWH1"}
        )
        cls.location = cls.warehouse.lot_stock_id
        cls.quant_obj = cls.env["stock.quant"]

    def test_stock_picking_filter_lot(self):
        # When a lot is initially created, no locations are available
        lot_1 = self.env["stock.production.lot"].create(
            {
                "name": "Test lot #1",
                "product_id": self.product.id,
                "company_id": self.env.company.id,
            }
        )
        self.assertEqual(len(lot_1.location_ids), 0)

        # Makes a location available
        quant_1 = self.quant_obj.create(
            {
                "product_id": self.product.id,
                "quantity": 10.0,
                "location_id": self.location.id,
                "lot_id": lot_1.id,
            }
        )
        self.assertEqual(len(lot_1.location_ids), 1)
        self.assertEqual(lot_1.location_ids, self.location)

        # A zero inventory adjustment makes locations unavailable again
        quant_1.quantity = 0
        self.assertEqual(len(lot_1.location_ids), 0)
