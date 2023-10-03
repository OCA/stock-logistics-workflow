# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import SavepointCase


class TestSearchLotProductQty(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.lot_model = cls.env["stock.production.lot"]
        cls.quant_model = cls.env["stock.quant"]
        cls.loc_stock = cls.env.ref("stock.stock_location_stock")
        cls.loc_output = cls.env.ref("stock.stock_location_output")
        cls.loc_output.active = True
        cls.loc_customers = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env.ref("stock.product_cable_management_box")
        cls.delivery_order_picking_type = cls.env.ref("stock.picking_type_out")
        cls.lot_1 = cls._create_lot(cls.product, "001")

    @classmethod
    def _create_lot(cls, product, lot_name):
        return cls.env["stock.production.lot"].create(
            {
                "name": lot_name,
                "product_id": product.id,
                "company_id": cls.env.company.id,
            }
        )

    @classmethod
    def _create_quant(cls, lot, location, qty):
        cls.quant_model._update_available_quantity(
            lot.product_id, location, qty, lot_id=lot
        )

    def test_compute_qty_location(self):
        self.assertFalse(self.lot_1.location_ids)
        self.assertFalse(self.lot_1.qty_available)

        self._create_quant(self.lot_1, self.loc_stock, 5)
        self.lot_1.flush()
        self.assertEqual(self.lot_1.location_ids, self.loc_stock)
        self.assertEqual(self.lot_1.qty_available, 5)

        # ignored because it's the wrong type of location
        self._create_quant(self.lot_1, self.loc_customers, 10)
        self.lot_1.flush()
        self.assertEqual(self.lot_1.location_ids, self.loc_stock)
        self.assertEqual(self.lot_1.qty_available, 5)

        self._create_quant(self.lot_1, self.loc_output, 15)
        self.lot_1.flush()
        self.assertEqual(self.lot_1.location_ids, self.loc_stock + self.loc_output)
        self.assertEqual(self.lot_1.qty_available, 20)

    def test_search_lot_with_qty(self):
        self._create_quant(self.lot_1, self.loc_stock, 5)

        lot_2 = self._create_lot(self.product, "002")
        self._create_quant(lot_2, self.loc_output, 10)

        self._create_lot(self.product, "003")

        search = self.lot_model.search(
            [("product_id", "=", self.product.id), ("product_qty", ">", 0)]
        )
        self.assertEqual(search, self.lot_1 + lot_2)

        search = self.lot_model.search(
            [("product_id", "=", self.product.id), ("product_qty", ">", 5)]
        )
        self.assertEqual(search, lot_2)
