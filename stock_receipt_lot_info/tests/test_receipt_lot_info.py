# Copyright 2022-24 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import timedelta

from odoo.fields import Datetime
from odoo.tests.common import TransactionCase


class ReceiptLotInfo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(ReceiptLotInfo, cls).setUpClass()
        group_stock_multi_locations = cls.env.ref("stock.group_stock_multi_locations")
        cls.env.user.write({"groups_id": [(4, group_stock_multi_locations.id, 0)]})
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        cls.product = cls.env["product.product"]
        cls.lot_model = cls.env["stock.lot"]
        cls.product_lot = cls.product.create(
            {
                "name": "Product A",
                "type": "product",
                "tracking": "lot",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )

        cls.lot1 = cls.lot_model.create(
            {
                "name": "lot_1",
                "product_id": cls.product_lot.id,
                "company_id": cls.env.company.id,
            }
        )

    def test_01_receipt_lot_info(self):
        """Test that info about dates in move lines is passed correctly
        to the new lot.
        """
        date = Datetime.now()
        receipt_type = self.env.ref("stock.picking_type_in")
        picking = self.env["stock.picking"].create(
            {
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "picking_type_id": receipt_type.id,
            }
        )
        move1 = self.env["stock.move"].create(
            {
                "name": "test_lot_info_1",
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "product_id": self.product_lot.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 1.0,
                "picking_id": picking.id,
                "picking_type_id": receipt_type.id,
            }
        )
        picking.action_confirm()
        move_line1 = move1.move_line_ids[0]
        move_line1.write(
            {
                "qty_done": 1,
                "lot_name": "lot1",
                "expiration_date": date + timedelta(days=15),
                "lot_use_date": date + timedelta(days=5),
                "lot_removal_date": date + timedelta(days=20),
                "lot_alert_date": date + timedelta(days=10),
            }
        )
        picking.button_validate()
        self.assertEqual(move1.state, "done")

        resulting_lot = self.lot_model.search(
            [("name", "=", "lot1"), ("product_id", "=", self.product_lot.id)]
        )
        self.assertTrue(resulting_lot)
        self.assertEqual(resulting_lot.expiration_date, date + timedelta(days=15))
        self.assertEqual(resulting_lot.use_date, date + timedelta(days=5))
        self.assertEqual(resulting_lot.removal_date, date + timedelta(days=20))
        self.assertEqual(resulting_lot.alert_date, date + timedelta(days=10))
