from datetime import datetime, timedelta

from odoo.addons.base.tests.common import BaseCommon


class TestStockPutawayLastLocation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.pack_location = cls.env.ref("stock.location_pack_zone")
        cls.pack_location.active = True
        cls.transit_location = cls.env["stock.location"].search(
            [
                ("company_id", "=", cls.env.company.id),
                ("usage", "=", "transit"),
                ("active", "=", False),
            ],
            limit=1,
        )
        cls.transit_location.active = True
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "consu",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "is_storable": True,
            }
        )
        cls.product_serial = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "consu",
                "tracking": "serial",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "is_storable": True,
            }
        )
        cls.product_lot = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "consu",
                "tracking": "lot",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "is_storable": True,
            }
        )
        cls.shelf_1_location = cls.env["stock.location"].create(
            {
                "name": "shelf_1",
                "usage": "internal",
                "location_id": cls.stock_location.id,
            }
        )
        cls.shelf_2_location = cls.env["stock.location"].create(
            {
                "name": "shelf_2",
                "usage": "internal",
                "location_id": cls.stock_location.id,
            }
        )
        cls.shelf_3_location = cls.env["stock.location"].create(
            {
                "name": "shelf_3",
                "usage": "internal",
                "location_id": cls.stock_location.id,
            }
        )
        cls.previous_move = cls.env["stock.move"].create(
            {
                "name": "Previous Move",
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.shelf_2_location.id,
                "product_id": cls.product.id,
                "product_uom": cls.uom_unit.id,
                "product_uom_qty": 10.0,
                "picked": True,
            }
        )
        cls.previous_move.quantity = 10.0
        cls.previous_move._action_done()

    def test_putaway_last_location_respects_rules(self):
        self.stock_location.putaway_default_to_last_location = True

        putaway = self.env["stock.putaway.rule"].create(
            {
                "category_id": self.env.ref("product.product_category_all").id,
                "location_in_id": self.stock_location.id,
                "location_out_id": self.shelf_1_location.id,
            }
        )
        self.stock_location.write({"putaway_rule_ids": [(4, putaway.id, 0)]})

        move = self.env["stock.move"].create(
            {
                "name": "Test Putaway",
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "product_id": self.product.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 10.0,
            }
        )
        move._action_confirm()
        self.assertEqual(move.state, "assigned")
        self.assertEqual(len(move.move_line_ids), 1)
        self.assertEqual(
            move.move_line_ids.location_dest_id.id, self.shelf_1_location.id
        )

    def test_putaway_last_location_no_location(self):
        self.previous_move.state = "draft"
        self.previous_move.unlink()
        self.stock_location.putaway_default_to_last_location = True

        move = self.env["stock.move"].create(
            {
                "name": "Test Putaway",
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "product_id": self.product.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 10.0,
            }
        )
        move._action_confirm()
        self.assertEqual(move.state, "assigned")
        self.assertEqual(len(move.move_line_ids), 1)
        self.assertEqual(move.move_line_ids.location_dest_id.id, self.stock_location.id)

    def test_putaway_last_location_last_location(self):
        self.stock_location.putaway_default_to_last_location = True
        self.assertEqual(self.previous_move.state, "done")
        move = self.env["stock.move"].create(
            {
                "name": "Test Putaway",
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "product_id": self.product.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 10.0,
            }
        )
        move._action_confirm()
        self.assertEqual(move.state, "assigned")
        self.assertEqual(len(move.move_line_ids), 1)
        self.assertEqual(
            move.move_line_ids.location_dest_id.id, self.shelf_2_location.id
        )

    def test_putaway_last_location_last_location_other_product(self):
        self.stock_location.putaway_default_to_last_location = True
        self.previous_move.state = "draft"
        self.previous_move.product_id = self.previous_move.move_line_ids.product_id = (
            self.env["product.product"].create(
                {
                    "name": "Product B",
                    "type": "consu",
                }
            )
        )
        self.previous_move.state = "done"

        move = self.env["stock.move"].create(
            {
                "name": "Test Putaway",
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "product_id": self.product.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 10.0,
            }
        )
        move._action_confirm()
        self.assertEqual(move.state, "assigned")
        self.assertEqual(len(move.move_line_ids), 1)
        self.assertEqual(move.move_line_ids.location_dest_id.id, self.stock_location.id)

    def test_putaway_last_location_ensure_last_location(self):
        self.stock_location.putaway_default_to_last_location = True

        previous_previous_move = self.env["stock.move"].create(
            {
                "name": "Previous Move",
                "location_id": self.supplier_location.id,
                "location_dest_id": self.shelf_3_location.id,
                "product_id": self.product.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 10.0,
                "picked": True,
            }
        )
        previous_previous_move.quantity = 10.0
        previous_previous_move._action_done()
        self.assertEqual(previous_previous_move.state, "done")
        self.assertEqual(len(previous_previous_move.move_line_ids), 1)
        self.assertEqual(
            previous_previous_move.move_line_ids.location_dest_id.id,
            self.shelf_3_location.id,
        )
        previous_previous_move.move_line_ids.date = datetime.now() - timedelta(days=1)

        move = self.env["stock.move"].create(
            {
                "name": "Test Putaway",
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "product_id": self.product.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 10.0,
            }
        )
        move._action_confirm()
        self.assertEqual(move.state, "assigned")
        self.assertEqual(len(move.move_line_ids), 1)
        self.assertEqual(
            move.move_line_ids.location_dest_id.id, self.shelf_2_location.id
        )

    def test_putaway_last_location_disabled(self):
        self.stock_location.putaway_default_to_last_location = False

        move = self.env["stock.move"].create(
            {
                "name": "Test Putaway",
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "product_id": self.product.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 10.0,
            }
        )
        move._action_confirm()
        self.assertEqual(move.state, "assigned")
        self.assertEqual(len(move.move_line_ids), 1)
        self.assertEqual(move.move_line_ids.location_dest_id.id, self.stock_location.id)
