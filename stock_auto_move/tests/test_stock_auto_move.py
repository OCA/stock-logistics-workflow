# Copyright 2014 NDP Systèmes (<https://www.ndp-systemes.fr>)
# Copyright 2020 ACSONE SA/NV (<https://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockAutoMove(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product_a1232 = cls.env.ref("product.product_product_6")
        cls.product_2 = cls.env.ref("product.product_product_9")
        cls.location_shelf = cls.env.ref("stock.stock_location_components")
        cls.location_1 = cls.env.ref("stock_auto_move.stock_location_a")
        cls.location_2 = cls.env.ref("stock_auto_move.stock_location_b")
        cls.location_3 = cls.env.ref("stock_auto_move.stock_location_c")
        cls.product_uom_unit_id = cls.env.ref("uom.product_uom_unit").id
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        cls.picking_type_id = cls.env.ref("stock.picking_type_internal").id
        cls.auto_group = cls.env.ref("stock_auto_move.automatic_group")
        cls.move_obj = cls.env["stock.move"]
        cls.procurement_group_obj = cls.env["procurement.group"]

    def test_10_auto_move(self):
        """Check automatic processing of move with auto_move set."""
        move = self.move_obj.create(
            {
                "name": "Test Auto",
                "product_id": self.product_a1232.id,
                "product_uom": self.product_uom_unit_id,
                "product_uom_qty": 12,
                "location_id": self.location_1.id,
                "location_dest_id": self.location_2.id,
                "picking_type_id": self.picking_type_id,
                "auto_move": True,
            }
        )
        move2 = self.move_obj.create(
            {
                "name": "Test Manual",
                "product_id": self.product_a1232.id,
                "product_uom": self.product_uom_unit_id,
                "product_uom_qty": 3,
                "location_id": self.location_1.id,
                "location_dest_id": self.location_2.id,
                "picking_type_id": self.picking_type_id,
                "auto_move": False,
            }
        )
        move._action_confirm()
        self.assertTrue(move.picking_id)
        self.assertEqual(move.group_id, self.auto_group)
        move2._action_confirm()
        self.assertTrue(move2.picking_id)
        self.assertFalse(move2.group_id)
        self.assertEqual(move.state, "confirmed")
        self.assertEqual(move2.state, "confirmed")
        move3 = self.move_obj.create(
            {
                "name": "Supply source location for test",
                "product_id": self.product_a1232.id,
                "product_uom": self.product_uom_unit_id,
                "product_uom_qty": 25,
                "location_id": self.location_shelf.id,
                "location_dest_id": self.location_1.id,
                "auto_move": False,
            }
        )
        move3._action_confirm()
        move3._action_assign()
        move3.quantity_done = move3.product_qty
        move3._action_done()
        move._action_assign()
        move2._action_assign()
        self.assertEqual(move3.state, "done")
        self.assertEqual(move2.state, "assigned")
        self.assertEqual(move.state, "done")

    def test_20_procurement_auto_move(self):
        """Check that move generated with procurement rule
        have auto_move set."""
        self.product_a1232.route_ids = [(4, self.ref("stock_auto_move.test_route"))]
        moves_before = self.move_obj.search([])
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_a1232,
                    1,
                    self.env.ref("uom.product_uom_unit"),
                    self.location_2,
                    "Test Procurement with auto_move",
                    "Test Procurement with auto_move",
                    self.env.company,
                    {
                        "warehouse_id": self.env.ref("stock.warehouse0"),
                        "date_planned": "2015-02-02 00:00:00",
                    },
                )
            ]
        )
        moves_after = self.move_obj.search([]) - moves_before
        self.assertEqual(
            moves_after.rule_id.id, self.ref("stock_auto_move.stock_rule_a_to_b"),
        )

        self.assertTrue(moves_after.auto_move)
        self.assertEqual(moves_after.state, "confirmed")
        self.assertEquals(moves_after.group_id, self.auto_group)

    def test_30_push_rule_auto(self):
        """Checks that push rule with auto set leads to an auto_move."""
        self.product_a1232.route_ids = [(4, self.ref("stock_auto_move.test_route"))]
        move3 = self.move_obj.create(
            {
                "name": "Supply source location for test",
                "product_id": self.product_a1232.id,
                "product_uom": self.product_uom_unit_id,
                "product_uom_qty": 7,
                "location_id": self.location_shelf.id,
                "location_dest_id": self.location_3.id,
                "auto_move": False,
            }
        )
        move3._action_confirm()
        move3._action_assign()
        move3._auto_assign_quantities()
        move3._action_done()
        quants_in_3 = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.product_a1232.id),
                ("location_id", "=", self.location_3.id),
            ]
        )
        quants_in_1 = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.product_a1232.id),
                ("location_id", "=", self.location_1.id),
            ]
        )
        self.assertEqual(len(quants_in_3), 0)
        self.assertGreater(len(quants_in_1), 0)

    def test_40_chained_auto_move(self):
        """
        Test case:
            - product with tracking set to serial.
            - warehouse reception steps set to two steps.
            - the push rule on the reception route set to auto move.
            - create movement using the reception picking type.
        Expected Result:
            The second step movement should be processed automatically
            after processing the first movement.
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.reception_steps = "two_steps"
        warehouse.reception_route_id.rule_ids.auto_move = True
        warehouse.int_type_id.use_create_lots = False
        warehouse.int_type_id.use_existing_lots = True

        picking = (
            self.env["stock.picking"]
            .with_context(default_picking_type_id=warehouse.in_type_id.id)
            .create(
                {
                    "partner_id": self.env.ref("base.res_partner_1").id,
                    "picking_type_id": warehouse.in_type_id.id,
                    "group_id": self.auto_group.id,
                    "location_id": self.env.ref("stock.stock_location_suppliers").id,
                }
            )
        )

        move1 = self.env["stock.move"].create(
            {
                "name": "Supply source location for test",
                "product_id": self.product_a1232.id,
                "product_uom": self.product_uom_unit_id,
                "product_uom_qty": 2,
                "picking_id": picking.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": warehouse.wh_input_stock_loc_id.id,
                "picking_type_id": warehouse.in_type_id.id,
            }
        )
        picking.action_confirm()
        self.assertTrue(picking.move_line_ids)
        self.assertEqual(len(picking.move_line_ids), 1)
        picking.move_line_ids.qty_done = 2
        picking.action_done()
        self.assertTrue(move1.move_dest_ids)

        self.assertTrue(move1.move_dest_ids.auto_move)
        self.assertEqual(move1.move_dest_ids.state, "done")

    def test_50_partial_chained_auto_move(self):
        """
        Test case:
            - product with tracking set to serial.
            - warehouse reception steps set to two steps.
            - the push rule on the reception route set to auto move.
            - create picking using the reception picking type.
            - do partial reception on first step
        Expected Result:
            The second step movement should be processed automatically
            and a back order is created.
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.reception_steps = "two_steps"
        warehouse.reception_route_id.rule_ids.auto_move = True
        warehouse.int_type_id.use_create_lots = False
        warehouse.int_type_id.use_existing_lots = True

        picking = (
            self.env["stock.picking"]
            .with_context(default_picking_type_id=warehouse.in_type_id.id)
            .create(
                {
                    "partner_id": self.env.ref("base.res_partner_1").id,
                    "picking_type_id": warehouse.in_type_id.id,
                    "group_id": self.auto_group.id,
                    "location_id": self.env.ref("stock.stock_location_suppliers").id,
                }
            )
        )

        move1 = self.env["stock.move"].create(
            {
                "name": "Supply source location for test",
                "product_id": self.product_a1232.id,
                "product_uom": self.product_uom_unit_id,
                "product_uom_qty": 2,
                "picking_id": picking.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": warehouse.wh_input_stock_loc_id.id,
                "picking_type_id": warehouse.in_type_id.id,
            }
        )
        picking.action_confirm()
        self.assertTrue(picking.move_line_ids)
        self.assertEqual(len(picking.move_line_ids), 1)
        picking.move_line_ids.qty_done = 1
        picking.move_line_ids.product_uom_qty = 1
        picking.action_done()

        # As move_dest_ids include backorders
        self.assertEqual(len(move1.move_dest_ids), 2)

        self.assertTrue(move1.move_dest_ids.mapped("auto_move"))
        move_done = move1.move_dest_ids.filtered(
            lambda m: not m.picking_id.backorder_id
        )
        self.assertEqual(move_done.state, "done")

        move_back = move1.move_dest_ids.filtered("picking_id.backorder_id")
        self.assertEqual(move_back.state, "waiting")

        # look up for the back order created
        back_order = self.env["stock.picking"].search(
            [("backorder_id", "=", picking.id)]
        )
        self.assertTrue(back_order)
        self.assertEqual(len(back_order), 1)

        back_order.move_line_ids.qty_done = 1
        back_order.action_done()

        move2 = back_order.move_lines
        self.assertEqual(len(move2.move_dest_ids), 2)

        self.assertEquals(move2.move_dest_ids.mapped("auto_move"), [True, True])
        self.assertEqual(move2.move_dest_ids.mapped("state"), ["done", "done"])

    def test_60_partial_chained_auto_move(self):
        """
        Test case:
            - product with tracking set to serial.
            - warehouse reception steps set to two steps.
            - create picking with two move lines.
            - set one of the move on the second step picking to be an auto
            move.
            - do partial reception on first step
        Expected Result:
            The second step movement should be processed automatically
            and a back order is created with the product that is not set as an
            auto move.
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.reception_steps = "two_steps"
        warehouse.reception_route_id.rule_ids.auto_move = True
        warehouse.int_type_id.use_create_lots = False
        warehouse.int_type_id.use_existing_lots = True

        picking = (
            self.env["stock.picking"]
            .with_context(default_picking_type_id=warehouse.in_type_id.id)
            .create(
                {
                    "partner_id": self.env.ref("base.res_partner_1").id,
                    "picking_type_id": warehouse.in_type_id.id,
                    "group_id": self.auto_group.id,
                    "location_id": self.env.ref("stock.stock_location_suppliers").id,
                }
            )
        )

        move1 = self.env["stock.move"].create(
            {
                "name": "Supply source location for test",
                "product_id": self.product_a1232.id,
                "product_uom": self.product_uom_unit_id,
                "product_uom_qty": 2,
                "picking_id": picking.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": warehouse.wh_input_stock_loc_id.id,
                "picking_type_id": warehouse.in_type_id.id,
            }
        )

        move2 = self.env["stock.move"].create(
            {
                "name": "Supply source location for test",
                "product_id": self.product_2.id,
                "product_uom": self.product_uom_unit_id,
                "product_uom_qty": 2,
                "picking_id": picking.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": warehouse.wh_input_stock_loc_id.id,
                "picking_type_id": warehouse.in_type_id.id,
            }
        )

        picking.action_confirm()
        self.assertTrue(move1.move_dest_ids.auto_move)
        self.assertTrue(move2.move_dest_ids.auto_move)
        second_step_picking = move2.move_dest_ids.picking_id
        move2.move_dest_ids.auto_move = False

        # do partial reception of the first picking
        move1.move_line_ids.qty_done = 2
        move1.move_line_ids.product_uom_qty = 2

        move2.move_line_ids.qty_done = 1
        move2.move_line_ids.product_uom_qty = 1

        picking.action_done()

        second_step_back_order = self.env["stock.picking"].search(
            [("backorder_id", "=", second_step_picking.id)]
        )

        self.assertEqual(second_step_picking.state, "done")
        self.assertEqual(len(second_step_picking.move_lines), 1)
        self.assertEqual(len(second_step_picking.move_line_ids), 1)

        self.assertEqual(len(second_step_back_order.move_lines), 1)
        self.assertTrue(
            second_step_back_order.move_lines.filtered(
                lambda m: m.state == "partially_available"
            )
        )

    def test_70_procurement_auto_move_keep_group(self):
        """Check that move generated with procurement rule
        have auto_move set."""
        self.product_a1232.route_ids = [(4, self.ref("stock_auto_move.test_route"))]
        moves_before = self.move_obj.search([])
        group_manual = self.env["procurement.group"].create({"name": "TEST MANUAL"})
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_a1232,
                    1,
                    self.env.ref("uom.product_uom_unit"),
                    self.location_2,
                    "Test Procurement with auto_move",
                    "Test Procurement with auto_move",
                    self.env.company,
                    {
                        "warehouse_id": self.env.ref("stock.warehouse0"),
                        "date_planned": "2015-02-02 00:00:00",
                        "group_id": group_manual,
                    },
                )
            ]
        )
        moves_after = self.move_obj.search([]) - moves_before
        self.assertEqual(
            moves_after.rule_id.id, self.ref("stock_auto_move.stock_rule_a_to_b"),
        )

        self.assertTrue(moves_after.auto_move)
        self.assertEqual(moves_after.state, "confirmed")
        self.assertEquals(moves_after.group_id, group_manual)

    def test_80_chained_auto_move_uom(self):
        """
        Test case:
            - product with tracking set to serial.
            - warehouse reception steps set to two steps.
            - the push rule on the reception route set to auto move.
            - create movement using the reception picking type.
            - Use the unit dozen => 24.0 total quantity
        Expected Result:
            The second step movement should be processed automatically
            after processing the first movement.
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.reception_steps = "two_steps"
        warehouse.reception_route_id.rule_ids.auto_move = True
        warehouse.int_type_id.use_create_lots = False
        warehouse.int_type_id.use_existing_lots = True

        picking = (
            self.env["stock.picking"]
            .with_context(default_picking_type_id=warehouse.in_type_id.id)
            .create(
                {
                    "partner_id": self.env.ref("base.res_partner_1").id,
                    "picking_type_id": warehouse.in_type_id.id,
                    "group_id": self.auto_group.id,
                    "location_id": self.env.ref("stock.stock_location_suppliers").id,
                }
            )
        )

        move1 = self.env["stock.move"].create(
            {
                "name": "Supply source location for test",
                "product_id": self.product_a1232.id,
                "product_uom": self.uom_dozen.id,
                "product_uom_qty": 2,
                "picking_id": picking.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": warehouse.wh_input_stock_loc_id.id,
                "picking_type_id": warehouse.in_type_id.id,
            }
        )
        picking.action_confirm()
        self.assertTrue(picking.move_line_ids)
        self.assertEqual(len(picking.move_line_ids), 1)
        picking.move_line_ids.qty_done = 2
        picking.action_done()
        self.assertTrue(move1.move_dest_ids)

        self.assertTrue(move1.move_dest_ids.auto_move)
        self.assertEqual(move1.move_dest_ids.state, "done")
        self.assertEqual(move1.move_dest_ids.quantity_done, 2.0)
        self.assertEqual(move1.move_dest_ids.product_qty, 24.0)

    def test_90_partial_chained_auto_move_no_backorder(self):
        """
        Test case:
            - product with tracking set to serial.
            - warehouse reception steps set to two steps.
            - create picking with two move lines.
            - do partial reception on first step with no backorder
        Expected Result:
            The second step movement should be processed automatically
            and the actual first quantity should be done
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.reception_steps = "two_steps"
        warehouse.reception_route_id.rule_ids.auto_move = True
        warehouse.int_type_id.use_create_lots = False
        warehouse.int_type_id.use_existing_lots = True

        picking = (
            self.env["stock.picking"]
            .with_context(default_picking_type_id=warehouse.in_type_id.id)
            .create(
                {
                    "partner_id": self.env.ref("base.res_partner_1").id,
                    "picking_type_id": warehouse.in_type_id.id,
                    "group_id": self.auto_group.id,
                    "location_id": self.env.ref("stock.stock_location_suppliers").id,
                }
            )
        )

        move1 = self.env["stock.move"].create(
            {
                "name": "Supply source location for test",
                "product_id": self.product_a1232.id,
                "product_uom": self.product_uom_unit_id,
                "product_uom_qty": 2,
                "picking_id": picking.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": warehouse.wh_input_stock_loc_id.id,
                "picking_type_id": warehouse.in_type_id.id,
                "propagate_cancel": True,
            }
        )

        move2 = self.env["stock.move"].create(
            {
                "name": "Supply source location for test",
                "product_id": self.product_2.id,
                "product_uom": self.product_uom_unit_id,
                "product_uom_qty": 2,
                "picking_id": picking.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": warehouse.wh_input_stock_loc_id.id,
                "picking_type_id": warehouse.in_type_id.id,
                "propagate_cancel": True,
            }
        )

        picking.action_confirm()
        self.assertTrue(move1.move_dest_ids.auto_move)
        self.assertTrue(move2.move_dest_ids.auto_move)
        second_step_picking = move2.move_dest_ids.picking_id

        # do partial reception of the first picking
        move1.move_line_ids.qty_done = 2
        move1.move_line_ids.product_uom_qty = 2

        move2.move_line_ids.qty_done = 1
        move2.move_line_ids.product_uom_qty = 1

        res = picking.button_validate()
        self.assertDictContainsSubset(
            {"res_model": "stock.backorder.confirmation"}, res,
        )
        wizard = self.env["stock.backorder.confirmation"].browse(res["res_id"])
        wizard.process_cancel_backorder()

        second_step_back_order = self.env["stock.picking"].search(
            [("backorder_id", "=", second_step_picking.id)]
        )

        self.assertFalse(second_step_back_order)

        self.assertEquals("done", move1.move_dest_ids.state)
        self.assertEquals("done", move2.move_dest_ids.state)
        self.assertEquals(2.0, move1.move_dest_ids.quantity_done)
        self.assertEquals(1.0, move2.move_dest_ids.quantity_done)

    def test_100_partial_chained_auto_move_mixed_no_backorder(self):
        """
        Test case:
            We do a two steps picking flow mixing products with auto move
            and no auto move.
            The procurement group is the same to simulate a picking flow
            for a purchase for instance.
            We transfer the first picking with partial quantities for both
            products and do not require backorder.
        Expected Result:
            The second step picking should be done for the auto move product
            and a backorder should have been generated for not yet transfered
            products. Indeed, a picking should not contain done movements with
            not yet done ones (and not cancelled).

        PICKING 1                           PICKING 2
            PRODUCT 1 (AUTO): 10 (5 done) =>    PRODUCT 1 (AUTO): 10
                                                    (5 done, 5 cancelled)
                                                ^
                                                | (backorder)
                                            PICKING 3
            PRODUCT 2: 10 (5 done)        =>    PRODUCT 2: 10 (5 partially ready)
        """
        vals = {"name": "PROCUREMENT PURCHASE TEST"}
        self.procurement = self.procurement_group_obj.create(vals)
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.reception_steps = "two_steps"
        warehouse.reception_route_id.rule_ids.action = "push"
        warehouse.reception_route_id.rule_ids.auto_move = True
        warehouse.int_type_id.use_create_lots = False
        warehouse.int_type_id.use_existing_lots = True

        # Create a second route for non automatic products
        route_manual = warehouse.reception_route_id.copy()
        route_manual.rule_ids.auto_move = False

        # Set product_2 to manual
        self.product_2.route_ids -= warehouse.reception_route_id
        self.product_2.route_ids |= route_manual

        picking = (
            self.env["stock.picking"]
            .with_context(default_picking_type_id=warehouse.in_type_id.id)
            .create(
                {
                    "partner_id": self.env.ref("base.res_partner_1").id,
                    "picking_type_id": warehouse.in_type_id.id,
                    "group_id": self.procurement.id,
                    "location_id": self.env.ref("stock.stock_location_suppliers").id,
                }
            )
        )

        move1 = self.env["stock.move"].create(
            {
                "name": "Supply source location for test",
                "product_id": self.product_a1232.id,
                "product_uom": self.product_uom_unit_id,
                "product_uom_qty": 10,
                "picking_id": picking.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": warehouse.wh_input_stock_loc_id.id,
                "picking_type_id": warehouse.in_type_id.id,
                "propagate_cancel": True,
                "group_id": self.procurement.id,
            }
        )

        move2 = self.env["stock.move"].create(
            {
                "name": "Supply source location for test",
                "product_id": self.product_2.id,
                "product_uom": self.product_uom_unit_id,
                "product_uom_qty": 10,
                "picking_id": picking.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": warehouse.wh_input_stock_loc_id.id,
                "picking_type_id": warehouse.in_type_id.id,
                "propagate_cancel": True,
                "group_id": self.procurement.id,
            }
        )

        picking.action_confirm()
        self.assertTrue(move1.move_dest_ids.auto_move)
        self.assertFalse(move2.move_dest_ids.auto_move)
        second_step_picking = move2.move_dest_ids.picking_id

        # do partial reception of the first picking
        move1.move_line_ids.qty_done = 5
        move1.move_line_ids.product_uom_qty = 5

        move2.move_line_ids.qty_done = 5
        move2.move_line_ids.product_uom_qty = 5

        res = picking.button_validate()
        self.assertDictContainsSubset(
            {"res_model": "stock.backorder.confirmation"}, res,
        )
        wizard = self.env["stock.backorder.confirmation"].browse(res["res_id"])
        wizard.process_cancel_backorder()

        # We need to ensure that all moves are done or cancelled in the
        # second picking
        self.assertItemsEqual(
            ["done", "cancel"],
            list(set(second_step_picking.move_lines.mapped("state"))),
        )

        # The second step picking should have a backorder for the
        # manual products
        second_step_back_order = self.env["stock.picking"].search(
            [("backorder_id", "=", second_step_picking.id)]
        )

        self.assertTrue(second_step_back_order)
        # If https://github.com/odoo/odoo/pull/66124 is integrated,
        # this should become assigned as remaining quantity should be cancelled
        # and quantities should be 5.0
        self.assertEquals(
            "partially_available", second_step_back_order.move_lines.state
        )
        self.assertEquals(10.0, second_step_back_order.move_lines.product_uom_qty)
