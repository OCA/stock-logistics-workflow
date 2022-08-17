# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestRestrictLot(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.output_loc = cls.env.ref("stock.stock_location_output")
        cls.product = cls.env.ref("product.product_product_16")
        cls.product.write({"tracking": "lot"})
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write({"delivery_steps": "pick_ship"})
        cls.lot = cls.env["stock.production.lot"].create(
            {
                "name": "lot1",
                "product_id": cls.product.id,
                "company_id": cls.warehouse.company_id.id,
            }
        )

    def test_move_restrict_lot_propagation(self):
        move = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "location_id": self.output_loc.id,
                "location_dest_id": self.customer_loc.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "name": "test",
                "procure_method": "make_to_order",
                "warehouse_id": self.warehouse.id,
                "route_ids": [(6, 0, self.warehouse.delivery_route_id.ids)],
                "restrict_lot_id": self.lot.id,
            }
        )
        move._action_confirm()
        orig_move = move.move_orig_ids
        self.assertEqual(orig_move.restrict_lot_id.id, self.lot.id)

    def test_move_split_and_copy(self):
        move = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "location_id": self.output_loc.id,
                "location_dest_id": self.customer_loc.id,
                "product_uom_qty": 2,
                "product_uom": self.product.uom_id.id,
                "name": "test",
                "procure_method": "make_to_stock",
                "warehouse_id": self.warehouse.id,
                "route_ids": [(6, 0, self.warehouse.delivery_route_id.ids)],
                "restrict_lot_id": self.lot.id,
            }
        )
        move._action_confirm()
        vals_list = move._split(1)
        new_move = self.env["stock.move"].create(vals_list)
        self.assertEqual(new_move.restrict_lot_id.id, move.restrict_lot_id.id)
        other_move = move.copy()
        self.assertFalse(other_move.restrict_lot_id.id)

    def _update_product_stock(self, qty, lot_id=False, location=None):
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Test Inventory",
                "product_ids": [(6, 0, self.product.ids)],
                "state": "confirm",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_qty": qty,
                            "location_id": location.id
                            if location
                            else self.warehouse.lot_stock_id.id,
                            "product_id": self.product.id,
                            "product_uom_id": self.product.uom_id.id,
                            "prod_lot_id": lot_id,
                        },
                    )
                ],
            }
        )
        inventory.action_validate()

    def test_move_restrict_lot_reservation(self):
        lot2 = self.env["stock.production.lot"].create(
            {
                "name": "lot2",
                "product_id": self.product.id,
                "company_id": self.warehouse.company_id.id,
            }
        )
        self._update_product_stock(1, lot2.id)

        move = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_dest_id": self.customer_loc.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "name": "test",
                "warehouse_id": self.warehouse.id,
                "restrict_lot_id": self.lot.id,
            }
        )
        move._action_confirm()
        move._action_assign()
        # move should not reserve wrong free lot
        self.assertEqual(move.state, "confirmed")

        self._update_product_stock(1, self.lot.id)
        move._action_assign()
        self.assertEqual(move.state, "assigned")
        self.assertEqual(move.move_line_ids.lot_id.id, self.lot.id)

    def test_procurement_with_2_steps_output(self):
        # make warehouse output in two step
        self.env["res.config.settings"].write(
            {
                "group_stock_adv_location": True,
                "group_stock_multi_locations": True,
            }
        )
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )
        warehouse.delivery_steps = "pick_ship"

        self.product.categ_id.route_ids |= self.env["stock.location.route"].search(
            [("name", "ilike", "deliver in 2")]
        )
        # self.env["stock.warehouse"].write(dict(delivery_steps='pick_ship',))
        location_1 = self.env["stock.location"].create(
            {"name": "loc1", "location_id": warehouse.lot_stock_id.id}
        )
        location_2 = self.env["stock.location"].create(
            {"name": "loc2", "location_id": warehouse.lot_stock_id.id}
        )

        # create goods in stock
        lot2 = self.env["stock.production.lot"].create(
            {
                "name": "lot 2",
                "product_id": self.product.id,
                "company_id": self.warehouse.company_id.id,
            }
        )
        self._update_product_stock(10, self.lot.id, location=location_1)
        self._update_product_stock(10, self.lot.id, location=location_2)
        self._update_product_stock(5, lot2.id, location=location_1)
        self._update_product_stock(25, lot2.id, location=location_2)

        # create a procurement with two lines of same product with different lots
        procurement_group = self.env["procurement.group"].create(
            {"name": "My procurement", "move_type": "one"}
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product,
                    15,
                    self.product.uom_id,
                    self.customer_loc,
                    "a name",
                    "an origin restrict on lot 1",
                    self.env.company,
                    {
                        "group_id": procurement_group,
                        "restrict_lot_id": self.lot.id,
                    },
                ),
                self.env["procurement.group"].Procurement(
                    self.product,
                    30,
                    self.product.uom_id,
                    self.customer_loc,
                    "a name",
                    "an origin restrict on lot 2",
                    self.env.company,
                    {
                        "group_id": procurement_group,
                        "restrict_lot_id": lot2.id,
                    },
                ),
            ]
        )
        # make sure in the two stock picking we get right quantities
        # for expected lot and locations

        def assert_move_qty_per_lot(moves, expect_lot, expect_qty):
            concern_move = moves.filtered(lambda mov: mov.restrict_lot_id == expect_lot)
            self.assertEqual(len(concern_move), 1)
            self.assertEqual(concern_move.product_uom_qty, expect_qty)

        def assert_move_line_per_lot_and_location(
            moves, expect_lot, expect_from_location, expect_reserved_qty
        ):
            concern_move_line = moves.filtered(
                lambda mov: mov.lot_id == expect_lot
                and mov.location_id == expect_from_location
            )
            self.assertEqual(len(concern_move_line), 1)
            self.assertEqual(concern_move_line.product_uom_qty, expect_reserved_qty)

        pickings = self.env["stock.picking"].search(
            [("group_id", "=", procurement_group.id)]
        )
        self.assertEqual(len(pickings), 2)
        delivery = pickings.filtered(
            lambda pick: pick.picking_type_id.code == "outgoing"
        )
        pick = pickings.filtered(lambda pick: pick.picking_type_id.code == "internal")

        self.assertEqual(delivery.state, "waiting")
        self.assertEqual(len(delivery.move_ids_without_package), 2)
        assert_move_qty_per_lot(delivery.move_ids_without_package, self.lot, 15)
        assert_move_qty_per_lot(delivery.move_ids_without_package, lot2, 30)

        pick.action_assign()
        self.assertEqual(pick.state, "assigned")
        self.assertEqual(len(pick.move_ids_without_package), 2)
        assert_move_qty_per_lot(pick.move_ids_without_package, self.lot, 15)
        assert_move_qty_per_lot(pick.move_ids_without_package, lot2, 30)
        assert_move_line_per_lot_and_location(
            pick.move_line_ids_without_package, self.lot, location_1, 10
        )
        assert_move_line_per_lot_and_location(
            pick.move_line_ids_without_package, self.lot, location_2, 5
        )
        assert_move_line_per_lot_and_location(
            pick.move_line_ids_without_package, lot2, location_1, 5
        )
        assert_move_line_per_lot_and_location(
            pick.move_line_ids_without_package, lot2, location_2, 25
        )
