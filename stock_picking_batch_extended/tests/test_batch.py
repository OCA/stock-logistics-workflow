# Copyright 2018 Tecnativa - Carlos Dauden
from odoo.exceptions import UserError
from odoo.tests import Form
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBatchPicking(TransactionCase):
    def _create_product(self, name, product_type="consu"):
        return self.env["product.product"].create({"name": name, "type": product_type})

    def setUp(self):
        super(TestBatchPicking, self).setUp()
        self.stock_loc = self.browse_ref("stock.stock_location_stock")
        self.customer_loc = self.browse_ref("stock.stock_location_customers")
        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.batch_model = self.env["stock.picking.batch"]
        # Delete (in transaction) all batches for simplify tests.
        self.batch_model.search([("state", "=", "draft")]).unlink()
        self.picking_model = self.env["stock.picking"]
        self.product6 = self._create_product("product_product_6")
        self.product7 = self._create_product("product_product_7")
        self.product8 = self._create_product("product_product_8", "product")
        self.product9 = self._create_product("product_product_9")
        self.product10 = self._create_product("product_product_10")
        self.product11 = self._create_product("product_product_11")
        self.picking = self.create_simple_picking(self.product6.ids + self.product7.ids)
        self.picking.action_confirm()
        self.picking2 = self.create_simple_picking((self.product9 + self.product10).ids)
        self.picking2.action_confirm()
        self.batch = self.batch_model.create(
            {
                "user_id": self.env.uid,
                "use_oca_batch_validation": True,
                "picking_ids": [(4, self.picking.id), (4, self.picking2.id)],
            }
        )

    def create_simple_picking(self, product_ids, batch_id=False):
        # The 'planned' context key ensures that the picking
        # will be created in the 'draft' state (no autoconfirm)
        return self.picking_model.with_context(planned=True).create(
            {
                "picking_type_id": self.ref("stock.picking_type_out"),
                "location_id": self.stock_loc.id,
                "location_dest_id": self.customer_loc.id,
                "batch_id": batch_id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": product_id,
                            "product_uom": self.ref("uom.product_uom_unit"),
                            "product_uom_qty": 1,
                            "location_id": self.stock_loc.id,
                            "location_dest_id": self.customer_loc.id,
                        },
                    )
                    for product_id in product_ids
                ],
            }
        )

    def test_assign__no_picking(self):
        batch = self.batch_model.create({})
        with self.assertRaises(UserError):
            batch.action_assign()

        # Even with multiple batches
        batches = batch | self.batch_model.create({})
        with self.assertRaises(UserError):
            for batch in batches:
                batch.action_assign()

    def test_assign(self):
        self.assertEqual("draft", self.batch.state)
        self.assertEqual("assigned", self.picking.state)
        self.assertEqual("assigned", self.picking2.state)
        self.assertEqual(4, len(self.batch.move_line_ids))
        self.assertEqual(4, len(self.batch.move_ids))

    def test_assign_with_cancel(self):
        self.picking2.action_cancel()
        self.assertEqual("draft", self.batch.state)
        self.assertEqual("assigned", self.picking.state)
        self.assertEqual("cancel", self.picking2.state)

        self.batch.action_assign()

        self.assertEqual("draft", self.batch.state)
        self.assertEqual("cancel", self.picking2.state)

    def test_cancel(self):
        self.assertEqual("draft", self.batch.state)
        self.assertEqual("assigned", self.picking.state)
        self.assertEqual("assigned", self.picking2.state)
        self.batch.action_cancel()

        self.assertEqual("cancel", self.batch.state)
        self.assertEqual("cancel", self.picking.state)
        self.assertEqual("cancel", self.picking2.state)

    def test_cancel__no_pickings(self):
        batch = self.batch_model.create({})
        self.assertEqual("draft", batch.state)
        batch.action_cancel()
        self.assertEqual("cancel", batch.state)

    def test_stock_picking_copy(self):
        picking = self.batch.picking_ids[0]
        self.assertEqual(self.batch, picking.batch_id)
        copy = picking.copy()
        self.assertFalse(copy.batch_id)

    def test_create_wizard(self):
        wizard = self.env["stock.picking.to.batch"].create(
            {"name": "Unittest wizard", "mode": "new"}
        )

        # Pickings already in batch.
        with self.assertRaises(UserError):
            wizard.with_context(active_ids=[self.picking.id]).action_create_batch()

        # Creating and selecting (too) another picking
        picking3 = self.create_simple_picking(self.product8.ids)
        picking3.action_confirm()

        self.assertEqual(
            0, self.batch_model.search_count([("name", "=", "Unittest wizard")])
        )

        wizard.with_context(
            active_ids=[self.picking.id, picking3.id]
        ).action_create_batch()

        batch = self.batch_model.search([("name", "=", "Unittest wizard")])
        self.assertEqual(1, len(batch))

        # Only picking3 because self.picking is already in another batch.
        self.assertEqual(picking3, batch.picking_ids)
        self.assertEqual(batch, picking3.batch_id)

    def test_wizard_user_id(self):
        wh_main = self.browse_ref("stock.warehouse0")

        wizard_model = self.env["stock.picking.to.batch"]
        wizard = wizard_model.create({"name": "Unittest wizard", "mode": "new"})
        self.assertFalse(wizard.user_id)

        wh_main.default_user_id = self.env.user

        wizard = wizard_model.create({"name": "Unittest wizard"})
        self.assertEqual(self.env.user, wizard.user_id)

        other_wh = self.env["stock.warehouse"].create(
            {"name": "Unittest other warehouse", "code": "UWH"}
        )

        wizard = wizard_model.with_context(warehouse_id=other_wh.id).create(
            {"name": "Unittest wizard"}
        )
        self.assertFalse(wizard.user_id)

        user2 = self.env["res.users"].create(
            {"name": "Unittest user", "login": "unittest_user"}
        )
        other_wh.default_user_id = user2
        wizard = wizard_model.with_context(warehouse_id=other_wh.id).create(
            {"name": "Unittest wizard"}
        )
        self.assertEqual(user2, wizard.user_id)

    def perform_action(self, action):
        model = action["res_model"]
        res_id = action["res_id"]
        res = self.env[model].browse(res_id)
        res = res.process()
        return res

    def test_backorder(self):
        # Change move lines quantities for product 6 and 7
        for move in self.batch.move_ids:
            if move.product_id == self.product6:
                move.product_uom_qty = 5
            elif move.product_id == self.product7:
                move.product_uom_qty = 2
        self.batch.action_assign()
        # Mark product 6 as partially processed and 7 and 9 as fully processed.
        for operation in self.batch.move_line_ids:
            # stock_move_line.qty_done
            if operation.product_id == self.product6:
                operation.qty_done = 3
            elif operation.product_id == self.product7:
                operation.qty_done = 2
            elif operation.product_id == self.product9:
                operation.qty_done = 1
        # confirm transfer action creation
        self.batch.action_assign()
        context = self.batch.action_done().get("context")
        # confirm transfer action creation
        Form(
            self.env["stock.backorder.confirmation"].with_context(**context)
        ).save().process()
        self.assertEqual("done", self.picking.state)
        self.assertEqual("done", self.picking2.state)
        # A backorder has been created for product with
        # 5 - 3 = 2 qty to process.
        backorder = self.picking_model.search([("backorder_id", "=", self.picking.id)])
        self.assertEqual(1, len(backorder))
        self.assertEqual("assigned", backorder.state)
        self.assertEqual(1, len(backorder.move_lines))
        self.assertEqual(self.product6, backorder.move_lines[0].product_id)
        self.assertEqual(2, backorder.move_lines[0].product_uom_qty)
        self.assertEqual(1, len(backorder.move_line_ids))
        self.assertEqual(2, backorder.move_line_ids[0].product_uom_qty)
        self.assertEqual(0, backorder.move_line_ids[0].qty_done)
        backorder2 = self.picking_model.search(
            [("backorder_id", "=", self.picking2.id)]
        )
        self.assertEqual(1, len(backorder2))
        self.assertEqual("assigned", backorder2.state)
        self.assertEqual(1, len(backorder2.move_lines))
        self.assertEqual(self.product10, backorder2.move_lines.product_id)
        self.assertEqual(1, backorder2.move_lines.product_uom_qty)
        self.assertEqual(1, len(backorder2.move_line_ids))
        self.assertEqual(1, backorder2.move_line_ids.product_uom_qty)
        self.assertEqual(0, backorder2.move_line_ids.qty_done)

    def test_assign_draft_pick(self):
        picking3 = self.create_simple_picking(
            self.product11.ids, batch_id=self.batch.id
        )
        self.assertEqual("draft", picking3.state)
        self.batch.action_assign()
        context = self.batch.action_done().get("context")
        Form(
            self.env["stock.immediate.transfer"].with_context(**context)
        ).save().process()
        self.assertEqual("done", self.batch.state)
        self.assertEqual("done", self.picking.state)
        self.assertEqual("done", self.picking2.state)
        self.assertEqual("done", picking3.state)

    def test_package(self):
        warehouse = self.browse_ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        group = self.env["procurement.group"].create(
            {"name": "Test", "move_type": "direct"}
        )
        values = {
            "company_id": warehouse.company_id,
            "group_id": group,
            "date_planned": "2018-11-13 12:12:59",
            "warehouse_id": warehouse,
        }
        procurements = [
            self.env["procurement.group"].Procurement(
                self.product11,
                1,
                self.env.ref("uom.product_uom_unit"),
                self.customer_loc,
                "test",
                "TEST",
                warehouse.company_id,
                values,
            )
        ]
        group.run(procurements)
        pickings = self.picking_model.search([("group_id", "=", group.id)])
        self.assertEqual(2, len(pickings))
        picking = pickings.filtered(lambda p: p.state == "assigned")
        picking.move_line_ids[0].qty_done = 1
        picking.action_put_in_pack()
        other_picking = pickings.filtered(lambda p: p.id != picking.id)
        picking._action_done()
        self.assertEqual("assigned", other_picking.state)
        # We add the 'package' picking in batch
        other_picking.batch_id = self.batch
        self.batch.action_assign()
        context = self.batch.action_done().get("context")
        Form(
            self.env["stock.immediate.transfer"].with_context(**context)
        ).save().process()
        self.assertEqual("done", self.batch.state)
        self.assertEqual("done", self.picking.state)
        self.assertEqual("done", self.picking2.state)
        self.assertEqual("done", other_picking.state)

    def test_remove_undone(self):
        self.picking2.action_cancel()
        self.assertEqual("assigned", self.picking.state)
        self.assertEqual("cancel", self.picking2.state)
        self.assertEqual("draft", self.batch.state)

        self.batch.remove_undone_pickings()

        self.assertEqual("cancel", self.batch.state)
        self.assertEqual(1, len(self.batch.picking_ids))
        self.assertEqual(self.picking2, self.batch.picking_ids)

    def test_partial_done(self):
        # If user filled some quantity_done manually in operations tab,
        # we want only these qties to be processed.
        # So picking with no qties processed are release and backorder are
        # created for picking partially processed.
        self.batch.action_assign()
        self.assertEqual("assigned", self.picking.state)
        self.assertEqual("assigned", self.picking2.state)
        self.picking.move_line_ids[0].qty_done = 1
        self.picking2.move_line_ids[0].qty_done = 1
        self.picking2.move_line_ids[1].qty_done = 1
        context = self.batch.action_done().get("context")
        # Create backorder? action
        Form(
            self.env["stock.backorder.confirmation"].with_context(**context)
        ).save().process()
        self.batch.remove_undone_pickings()
        self.assertEqual(len(self.batch.picking_ids), 2)
        self.assertEqual("done", self.picking.state)
        # Second picking is filled and his state is done too
        self.assertEqual("done", self.picking2.state)
        self.assertTrue(self.picking2.batch_id)
        picking_backorder = self.picking_model.search(
            [("backorder_id", "=", self.picking.id)]
        )
        self.assertEqual(1, len(picking_backorder.move_lines))

    def test_wizard_batch_grouped_by_field(self):
        Wiz = self.env["stock.picking.to.batch"]
        self.picking.origin = "A"
        self.picking2.origin = "B"
        pickings = self.picking + self.picking2

        wiz = Wiz.with_context(active_ids=pickings.ids).create(
            {"name": "Unittest wizard", "mode": "new"}
        )
        # Read values from config parameters, before first execution there
        # are no values
        self.assertFalse(wiz.batch_by_group)
        self.assertFalse(wiz.group_field_ids)

        # Add fields no to do one batch picking per grouped picking
        # create_date field
        origin_field = self.env.ref("stock.field_stock_picking__origin")
        wiz.batch_by_group = True
        wiz.group_field_ids = [(0, 0, {"sequence": 1, "field_id": origin_field.id})]
        # Raise error if any picking already is in other batch picking
        with self.assertRaises(UserError):
            wiz.action_create_batch()

        # Two picking has distinct origin so two batch pickings must be created
        pickings.write({"batch_id": False})
        res = wiz.action_create_batch()
        self.assertTrue(res["domain"])

        # Two picking has same origin so only one batch picking must be created
        pickings.write({"batch_id": False})
        self.picking2.origin = "A"
        res = wiz.action_create_batch()
        self.assertTrue(res["res_id"])

        # Test if group field create_date has been stored into config
        # parameters
        self.assertEqual(origin_field, wiz.load_store_fields())
