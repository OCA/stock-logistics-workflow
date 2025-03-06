from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestPacking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("lot_stock_id", "=", cls.stock_location.id)], limit=1
        )
        cls.warehouse.reception_steps = "two_steps"

        cls.productA = cls.env["product.product"].create(
            {"name": "Product A", "type": "product"}
        )

    def test_01_push_delay(self):
        """Checks that the push picking is delayed"""
        receipt_form = Form(self.env["stock.picking"])
        receipt_form.picking_type_id = self.warehouse.in_type_id
        with receipt_form.move_ids_without_package.new() as move_line:
            move_line.product_id = self.productA
            move_line.product_uom_qty = 1
        receipt = receipt_form.save()
        receipt.action_confirm()
        # Checks an internal transfer was not created.
        internal_transfer = self.env["stock.picking"].search(
            [("picking_type_id", "=", self.warehouse.int_type_id.id)],
            order="id desc",
            limit=1,
        )
        self.assertNotEqual(internal_transfer.origin, receipt.name)

        receipt._action_done()
        # Checks an internal transfer was created.
        internal_transfer = self.env["stock.picking"].search(
            [("picking_type_id", "=", self.warehouse.int_type_id.id)],
            order="id desc",
            limit=1,
        )
        self.assertEqual(internal_transfer.origin, receipt.name)

    def test_02_alternative_route(self):
        reception_route = self.warehouse.reception_route_id
        reception_route.rule_ids.write({"active": False})
        reception_type = self.warehouse.in_type_id
        reception_type.default_location_dest_id = self.warehouse.wh_input_stock_loc_id
        self.env["stock.rule"].create(
            {
                "name": "Receive",
                "route_id": reception_route.id,
                "location_src_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.warehouse.lot_stock_id.id,
                "action": "pull",
                "picking_type_id": reception_type.id,
                "procure_method": "make_to_stock",
                "warehouse_id": self.warehouse.id,
                "company_id": self.env.company.id,
                "location_dest_from_rule": False,
            }
        )
        self.env["stock.rule"].create(
            {
                "name": "Receive second step",
                "route_id": reception_route.id,
                "location_src_id": self.warehouse.wh_input_stock_loc_id.id,
                "location_dest_id": self.warehouse.lot_stock_id.id,
                "action": "push",
                "picking_type_id": reception_type.id,
                "procure_method": "make_to_stock",
                "warehouse_id": self.warehouse.id,
                "company_id": self.env.company.id,
            }
        )
        pre_pickings = self.env["stock.picking"].search([])
        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": self.productA.id,
                "warehouse_id": self.warehouse.id,
                "product_min_qty": 10,
                "product_max_qty": 20,
            }
        )

        orderpoint.action_replenish()
        post_pickings = self.env["stock.picking"].search([])
        self.assertEqual(len(pre_pickings) + 1, len(post_pickings))
        receive_picking = post_pickings - pre_pickings
        self.assertEqual(
            receive_picking.move_ids.location_dest_id,
            self.warehouse.wh_input_stock_loc_id,
        )
        self.assertEqual(
            receive_picking.move_ids.location_final_id, self.warehouse.lot_stock_id
        )
        self.assertEqual(
            receive_picking.move_ids.route_ids, self.warehouse.reception_route_id
        )
        for move in receive_picking.move_ids:
            move.quantity = move.product_qty
            move.picked = True

        receive_picking._action_done()
        new_post_pickings = self.env["stock.picking"].search([])
        self.assertEqual(len(post_pickings) + 1, len(new_post_pickings))
        receive_picking = new_post_pickings - post_pickings
        self.assertEqual(
            receive_picking.move_ids.location_dest_id, self.warehouse.lot_stock_id
        )

    def test_03_alternative_route_less_qty(self):
        reception_route = self.warehouse.reception_route_id
        reception_route.rule_ids.write({"active": False})
        reception_type = self.warehouse.in_type_id
        reception_type.default_location_dest_id = self.warehouse.wh_input_stock_loc_id
        self.env["stock.rule"].create(
            {
                "name": "Receive",
                "route_id": reception_route.id,
                "location_src_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.warehouse.lot_stock_id.id,
                "action": "pull",
                "picking_type_id": reception_type.id,
                "procure_method": "make_to_stock",
                "warehouse_id": self.warehouse.id,
                "company_id": self.env.company.id,
                "location_dest_from_rule": False,
            }
        )
        self.env["stock.rule"].create(
            {
                "name": "Receive second step",
                "route_id": reception_route.id,
                "location_src_id": self.warehouse.wh_input_stock_loc_id.id,
                "location_dest_id": self.warehouse.lot_stock_id.id,
                "action": "push",
                "picking_type_id": reception_type.id,
                "procure_method": "make_to_stock",
                "warehouse_id": self.warehouse.id,
                "company_id": self.env.company.id,
            }
        )
        pre_pickings = self.env["stock.picking"].search([])
        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": self.productA.id,
                "warehouse_id": self.warehouse.id,
                "product_min_qty": 10,
                "product_max_qty": 20,
            }
        )

        orderpoint.action_replenish()
        post_pickings = self.env["stock.picking"].search([])
        self.assertEqual(len(pre_pickings) + 1, len(post_pickings))
        receive_picking = post_pickings - pre_pickings
        self.assertEqual(
            receive_picking.move_ids.location_dest_id,
            self.warehouse.wh_input_stock_loc_id,
        )
        self.assertEqual(
            receive_picking.move_ids.location_final_id, self.warehouse.lot_stock_id
        )
        self.assertEqual(
            receive_picking.move_ids.route_ids, self.warehouse.reception_route_id
        )
        for move in receive_picking.move_ids:
            move.quantity = 5
            move.picked = True

        wizard_action = receive_picking.button_validate()
        context = wizard_action["context"]
        wizard = Form(self.env["stock.backorder.confirmation"].with_context(**context))
        confirm_dialog = wizard.save()
        confirm_dialog.process_cancel_backorder()

        new_post_pickings = self.env["stock.picking"].search([])
        self.assertEqual(len(post_pickings) + 1, len(new_post_pickings))
        receive_picking = new_post_pickings - post_pickings
        self.assertEqual(
            receive_picking.move_ids.location_dest_id, self.warehouse.lot_stock_id
        )
        self.assertEqual(receive_picking.move_ids.product_uom_qty, 5)
