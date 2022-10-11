# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestOperationQuickChange(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Location = self.env["stock.location"]
        self.PickingType = self.env["stock.picking.type"]
        self.Picking = self.env["stock.picking"]
        self.Product = self.env["product.template"]
        self.Wizard = self.env["stock.picking.operation.wizard"]
        self.warehouse = self.env["stock.warehouse"].create(
            {"name": "warehouse - test", "code": "WH-TEST"}
        )

        # self.warehouse.lot_stock_id.id
        self.product = self.Product.create(
            {
                "name": "Product - Test",
                "type": "product",
                "list_price": 100.00,
                "standard_price": 100.00,
            }
        )
        self.qty_on_hand(self.product.product_variant_ids)
        self.product2 = self.Product.create(
            {
                "name": "Product2 - Test",
                "type": "product",
                "list_price": 100.00,
                "standard_price": 100.00,
            }
        )
        self.qty_on_hand(self.product2.product_variant_ids)
        self.customer = self.env["res.partner"].create({"name": "Customer - test"})
        self.picking_type = self.PickingType.search(
            [("warehouse_id", "=", self.warehouse.id), ("code", "=", "outgoing")]
        )
        self.picking = self.Picking.create(
            {
                "name": "picking - test 01",
                "location_id": self.warehouse.lot_stock_id.id,
                "location_dest_id": self.warehouse.wh_output_stock_loc_id.id,
                "picking_type_id": self.picking_type.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.product_variant_ids.id,
                            "product_uom_qty": 20.0,
                            "product_uom": self.product.uom_id.id,
                            "location_id": self.warehouse.lot_stock_id.id,
                            "location_dest_id": self.warehouse.wh_output_stock_loc_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product2.product_variant_ids.id,
                            "product_uom_qty": 60.0,
                            "product_uom": self.product.uom_id.id,
                            "location_id": self.warehouse.lot_stock_id.id,
                            "location_dest_id": self.warehouse.wh_output_stock_loc_id.id,
                        },
                    ),
                ],
            }
        )

    def qty_on_hand(self, product):
        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "inventory_quantity": 200,
                "location_id": self.warehouse.lot_stock_id.id,
            }
        )._apply_inventory()

    def test_picking_operation_change_location_dest_all(self):
        self.picking.action_assign()
        new_location_dest_id = self.Location.create(
            {
                "name": "New Test Customer Location",
                "location_id": self.picking.location_dest_id.location_id.id,
            }
        )
        wiz = self.Wizard.with_context(
            active_model=self.picking._name,
            active_ids=self.picking.ids,
        ).create({"new_location_dest_id": new_location_dest_id.id, "change_all": True})
        move_lines = self.picking.mapped("move_line_ids")
        self.assertEqual(wiz.location_dest_id, self.picking.location_dest_id)
        self.assertEqual(wiz.old_location_dest_id, move_lines[:1].location_dest_id)
        wiz.action_apply()
        move_lines = self.picking.mapped("move_line_ids.location_dest_id")
        self.assertEqual(len(move_lines), 1)

    def test_picking_operation_change_location_dest(self):
        new_location_dest_id = self.Location.create(
            {
                "name": "New Test Customer Location",
                "location_id": self.picking.location_dest_id.location_id.id,
            }
        )
        other_location_dest_id = self.Location.create(
            {
                "name": "New Test Customer Location",
                "location_id": self.picking.location_dest_id.location_id.id,
            }
        )
        self.picking.action_assign()
        move_lines = self.picking.mapped("move_line_ids")
        move_lines[:1].write({"location_dest_id": other_location_dest_id.id})
        wiz = self.Wizard.with_context(
            active_model=self.picking._name,
            active_ids=self.picking.ids,
        ).create(
            {
                "old_location_dest_id": self.picking.location_dest_id.id,
                "new_location_dest_id": new_location_dest_id.id,
            }
        )
        wiz.action_apply()
        move_lines = self.picking.mapped("move_line_ids.location_dest_id")
        self.assertEqual(len(move_lines), 2)

    def test_picking_operation_change_location_dest_failed(self):
        self.picking.action_assign()
        for move in self.picking.move_lines:
            move.quantity_done = 1
        self.picking._action_done()
        new_location_dest_id = self.Location.create(
            {
                "name": "New Test Customer Location",
                "location_id": self.picking.location_dest_id.location_id.id,
            }
        )
        wiz = self.Wizard.with_context(
            active_model=self.picking._name,
            active_ids=self.picking.ids,
        ).create({"new_location_dest_id": new_location_dest_id.id, "change_all": True})
        with self.assertRaises(UserError):
            wiz.action_apply()
