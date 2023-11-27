from odoo.tests import SavepointCase


class TestStockPickingReturnRestrictLot(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        grp_multi_loc = cls.env.ref("stock.group_stock_multi_locations")
        grp_multi_step_rule = cls.env.ref("stock.group_adv_location")
        grp_pack = cls.env.ref("stock.group_tracking_lot")

        cls.env.user.groups_id |= grp_multi_loc | grp_multi_step_rule | grp_pack

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write(
            {
                "delivery_steps": "pick_ship",
            }
        )
        cls.supplier_loc = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.wh_stock_loc = cls.warehouse.lot_stock_id
        cls.wh_picking_type_in = cls.warehouse.in_type_id
        cls.wh_picking_type_in.use_create_lots = False
        cls.wh_picking_type_in.use_existing_lots = True
        cls.wh_picking_type_in.show_operations = True
        cls.wh_picking_type_in.show_reserved = False

        cls.wh_stock_sub_loc_A = cls.env["stock.location"].create(
            {
                "name": "WH - A",
                "barcode": "A",
                "usage": "internal",
                "location_id": cls.wh_stock_loc.id,
            }
        )
        cls.wh_stock_sub_loc_B = cls.env["stock.location"].create(
            {
                "name": "WH - B",
                "barcode": "B",
                "usage": "internal",
                "location_id": cls.wh_stock_loc.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product name",
                "default_code": "CODE",
                "type": "product",
                "tracking": "lot",
                "route_ids": [
                    (
                        4,
                        cls.warehouse.route_ids.filtered(
                            lambda r: "(pick + ship)" in r.name
                        ).id,
                    )
                ],
            }
        )
        cls.lot = cls.env["stock.production.lot"].create(
            {
                "name": "lot test",
                "product_id": cls.product.id,
                "company_id": cls.warehouse.company_id.id,
            }
        )
        cls.lot2 = cls.env["stock.production.lot"].create(
            {
                "name": "lot test 2",
                "product_id": cls.product.id,
                "company_id": cls.warehouse.company_id.id,
            }
        )
        cls.lot3 = cls.env["stock.production.lot"].create(
            {
                "name": "lot test 3",
                "product_id": cls.product.id,
                "company_id": cls.warehouse.company_id.id,
            }
        )

        inventory = cls.env["stock.inventory"].create(
            {
                "name": "Populate some stock",
                "product_ids": [(6, 0, cls.product.ids)],
                "state": "confirm",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_qty": 10,
                            "location_id": cls.wh_stock_loc.id,
                            "product_id": cls.product.id,
                            "product_uom_id": cls.product.uom_id.id,
                            "prod_lot_id": cls.lot.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_qty": 5,
                            "location_id": cls.wh_stock_loc.id,
                            "product_id": cls.product.id,
                            "product_uom_id": cls.product.uom_id.id,
                            "prod_lot_id": cls.lot2.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_qty": 10,
                            "location_id": cls.wh_stock_sub_loc_A.id,
                            "product_id": cls.product.id,
                            "product_uom_id": cls.product.uom_id.id,
                            "prod_lot_id": cls.lot3.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_qty": 10,
                            "location_id": cls.wh_stock_sub_loc_B.id,
                            "product_id": cls.product.id,
                            "product_uom_id": cls.product.uom_id.id,
                            "prod_lot_id": cls.lot3.id,
                        },
                    ),
                ],
            }
        )
        inventory.action_validate()

        cls.receipt = cls.env["stock.picking"].create(
            {
                "move_type": "direct",
                "location_id": cls.supplier_loc.id,
                "location_dest_id": cls.wh_stock_loc.id,
                "picking_type_id": cls.wh_picking_type_in.id,
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "name": cls.product.display_name,
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 5,
                "location_id": cls.supplier_loc.id,
                "location_dest_id": cls.wh_stock_loc.id,
                "picking_id": cls.receipt.id,
            }
        )
        cls.receipt.action_confirm()
        cls.receipt.action_assign()
        cls.receipt.move_line_ids.lot_id = cls.lot
        cls.receipt.move_line_ids.qty_done = 2
        # assume there is kind of put away rules
        cls.receipt.move_line_ids.location_dest_id = cls.wh_stock_sub_loc_A

        cls.receipt.move_line_ids |= cls.env["stock.move.line"].create(
            {
                "move_id": cls.move.id,
                "product_id": cls.product.id,
                "product_uom_id": cls.product.uom_id.id,
                "qty_done": 3,
                "lot_id": cls.lot2.id,
                "location_id": cls.supplier_loc.id,
                # assume there is kind of put away rules
                "location_dest_id": cls.wh_stock_sub_loc_B.id,
            }
        )
        cls.receipt._action_done()

        # generate 2 steps deliveries

        cls.picking, cls.delivery = cls._generate_picking_and_delivery()
        cls.picking.action_assign()

    @classmethod
    def _generate_picking_and_delivery(
        cls, location=None, qty_per_lot=None, product=None
    ):
        if not product:
            product = cls.product
        if not location:
            location = cls.customer_loc
        if not qty_per_lot:
            qty_per_lot = [{"lot": cls.lot, "quantity": 10}]

        procurements = []
        group = cls.env["procurement.group"].create(
            {"name": location.name, "move_type": "one"}
        )
        for product_need in qty_per_lot:
            procurements.append(
                cls.env["procurement.group"].Procurement(
                    product,
                    product_need["quantity"],
                    product.uom_id,
                    location,
                    group.name,
                    "Test delivery",
                    cls.env.company,
                    {
                        "group_id": group,
                        "restrict_lot_id": product_need["lot"].id,
                    },
                )
            )

        cls.env["procurement.group"].run(procurements)
        return (
            group.stock_move_ids.picking_id.filtered(
                lambda pick: pick.picking_type_id.code == "internal"
            ),
            group.stock_move_ids.picking_id.filtered(
                lambda pick: pick.picking_type_id.code == "outgoing"
            ),
        )

    def assert_product_quantity(
        self, location, lot, expected_quantity, product=None, qty_field="quantity"
    ):
        if not product:
            product = self.product

        quantity = sum(
            self.env["stock.quant"]
            .search(
                [
                    ("location_id", "=", location.id),
                    ("product_id", "=", product.id),
                    ("lot_id", "=", lot.id),
                ],
            )
            .mapped(qty_field)
        )
        self.assertEqual(
            expected_quantity,
            quantity,
            f"Expected {expected_quantity} {qty_field} in {location.name} "
            f"on product {product.name} with lot '{lot.name}' but found {quantity}",
        )

    def test_action_stock_picking_full_return(self):
        action = self.receipt.action_stock_picking_full_return()
        self.assertEqual(action["name"], "Returned Picking")
        self.assertNotEqual(action["res_id"], self.receipt.id)
        return_picking = self.env["stock.picking"].browse(action["res_id"])
        self.assertEqual(return_picking.state, "assigned")
        self.assertEqual(
            return_picking.picking_type_id,
            self.receipt.picking_type_id.return_picking_type_id,
        )
        self.assertEqual(return_picking.location_id, self.wh_stock_loc)
        self.assertEqual(return_picking.location_dest_id, self.supplier_loc)
        self.assertEqual(
            return_picking.move_line_ids.filtered(
                lambda line, lot=self.lot: line.lot_id == lot
            ).product_uom_qty,
            2,
        )
        self.assertEqual(
            return_picking.move_line_ids.filtered(
                lambda line, lot=self.lot2: line.lot_id == lot
            ).product_uom_qty,
            3,
        )

    def test_multi_action_stock_picking_full_return(self):
        receipt2 = self.receipt.copy()
        receipt2.action_confirm()
        receipt2.action_assign()
        receipt2.move_line_ids.lot_id = self.lot3
        receipt2.move_line_ids.qty_done = 5

        receipt2._action_done()

        action = (self.receipt | receipt2).action_stock_picking_full_return()

        self.assertEqual(action["name"], "Returned Picking")
        self.assertEqual(len(action["domain"][0][2]), 2)

    def test_returning_picking_cancel_delivery_reservation(self):
        self.picking.move_line_ids.qty_done = 10
        self.picking._action_done()
        self.assert_product_quantity(self.picking.location_dest_id, self.lot, 10)
        self.assertEqual(self.delivery.state, "assigned")
        self.assert_product_quantity(
            self.picking.location_dest_id, self.lot, 10, qty_field="reserved_quantity"
        )
        action = self.picking.action_stock_picking_full_return()
        return_picking = self.env["stock.picking"].browse(action["res_id"])
        self.assertEqual(return_picking.move_lines.product_uom_qty, 10)
        self.assert_product_quantity(self.picking.location_dest_id, self.lot, 10)
        self.assertEqual(self.delivery.state, "confirmed")
        return_picking.move_line_ids.qty_done = 10
        return_picking._action_done()
        self.assert_product_quantity(self.picking.location_id, self.lot, 10)

    def test_returning_picking_with_partial_delivered_no_backorder(self):
        self.picking.move_line_ids.qty_done = 10
        self.picking._action_done()
        self.assert_product_quantity(self.picking.location_dest_id, self.lot, 10)
        self.delivery.move_line_ids.qty_done = 6
        self.delivery.with_context(cancel_backorder=True)._action_done()
        self.assert_product_quantity(self.picking.location_dest_id, self.lot, 4)
        self.assert_product_quantity(
            self.picking.location_dest_id, self.lot, 0, qty_field="reserved_quantity"
        )
        action = self.picking.action_stock_picking_full_return()
        return_picking = self.env["stock.picking"].browse(action["res_id"])
        self.assertEqual(return_picking.move_lines.product_uom_qty, 10)
        self.assertEqual(self.delivery.state, "done")
        self.assertEqual(return_picking.move_line_ids.product_uom_qty, 4)
        return_picking.move_line_ids.qty_done = 4
        return_picking._action_done()
        self.assert_product_quantity(self.picking.location_id, self.lot, 4)
        self.assert_product_quantity(self.customer_loc, self.lot, 6)

    def test_returning_picking_with_partial_delivered_with_backorder(self):
        self.picking.move_line_ids.qty_done = 10
        self.picking._action_done()
        self.assert_product_quantity(self.picking.location_dest_id, self.lot, 10)
        self.delivery.move_line_ids.qty_done = 4
        self.delivery.with_context(cancel_backorder=False)._action_done()
        self.assert_product_quantity(self.picking.location_dest_id, self.lot, 6)
        delivery_backorder = self.delivery.backorder_ids
        self.assertEqual(delivery_backorder.state, "assigned")
        self.assert_product_quantity(
            self.picking.location_dest_id, self.lot, 6, qty_field="reserved_quantity"
        )
        action = self.picking.action_stock_picking_full_return()
        return_picking = self.env["stock.picking"].browse(action["res_id"])
        self.assertEqual(return_picking.move_lines.product_uom_qty, 10)
        self.assert_product_quantity(self.picking.location_dest_id, self.lot, 6)
        self.assertEqual(self.delivery.state, "done")
        self.assertEqual(delivery_backorder.state, "confirmed")
        self.assertEqual(return_picking.move_line_ids.product_uom_qty, 6)
        return_picking.move_line_ids.qty_done = 6
        return_picking._action_done()
        self.assert_product_quantity(self.picking.location_id, self.lot, 6)
        self.assert_product_quantity(self.customer_loc, self.lot, 4)

    def test_returning_picking_with_full_delivered_quantities(self):
        self.picking.move_line_ids.qty_done = 10
        self.picking._action_done()
        self.assert_product_quantity(self.picking.location_dest_id, self.lot, 10)
        self.delivery.move_line_ids.qty_done = 10
        self.delivery._action_done()
        self.assert_product_quantity(self.customer_loc, self.lot, 10)
        action = self.picking.action_stock_picking_full_return()
        return_picking = self.env["stock.picking"].browse(action["res_id"])
        self.assertEqual(
            return_picking.move_lines.move_orig_ids, self.picking.move_lines
        )
        self.assertEqual(
            return_picking.move_lines.move_dest_ids, self.env["stock.move"].browse()
        )
        self.assertEqual(return_picking.state, "waiting")
        self.assertEqual(return_picking.move_lines.product_uom_qty, 10)

    def test_return_twice(self):
        self.picking.move_line_ids.qty_done = 10
        self.picking._action_done()
        action = self.picking.action_stock_picking_full_return()
        return_picking = self.env["stock.picking"].browse(action["res_id"])
        return_picking.move_line_ids.qty_done = 10
        return_picking._action_done()
        action = return_picking.action_stock_picking_full_return()
        re_pick = self.env["stock.picking"].browse(action["res_id"])
        self.assertEqual(re_pick.move_lines.move_orig_ids, return_picking.move_lines)
        # not sure adding return picking move as dest make a lot of sense here
        # but mainly copy / paste the behaviour from odoo return wizard
        self.assertEqual(
            re_pick.move_lines.move_dest_ids,
            (return_picking.move_lines | self.delivery.move_lines),
        )
        re_pick.move_line_ids.qty_done = 10
        re_pick._action_done()
        self.assertEqual(self.delivery.state, "assigned")

    def test_return_a_partial_with_nil_qty_done(self):
        # this sounds weird as it's done in setupClass
        self.product.write(
            {
                "route_ids": [
                    (
                        4,
                        self.warehouse.route_ids.filtered(
                            lambda r: "(pick + ship)" in r.name
                        ).id,
                    )
                ],
            }
        )

        picking, delivery = self._generate_picking_and_delivery(
            qty_per_lot=[
                {"lot": self.lot2, "quantity": 2},
                {"lot": self.lot3, "quantity": 3},
            ],
            location=self.customer_loc,
            product=self.product,
        )
        picking.action_assign()
        picking.move_line_ids.filtered(
            lambda l, lot=self.lot2: l.lot_id == lot
        ).qty_done = 2
        picking.with_context(cancel_backorder=True)._action_done()
        self.assertEqual(
            picking.move_lines.filtered(
                lambda l, lot=self.lot3: l.restrict_lot_id == lot
            ).state,
            "cancel",
        )
        action = picking.action_stock_picking_full_return()
        return_picking = self.env["stock.picking"].browse(action["res_id"])
        return_picking.move_lines.product_uom_qty = 2
