# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestStockMoveChangeSourceLocation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockMoveChangeSourceLocation, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.Location = cls.env["stock.location"]
        cls.PickingType = cls.env["stock.picking.type"]
        cls.Picking = cls.env["stock.picking"]
        cls.Product = cls.env["product.template"]
        cls.Wizard = cls.env["stock.move.change.source.location.wizard"]
        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "warehouse - test", "code": "WH-TEST"}
        )

        # cls.warehouse.lot_stock_id.id
        cls.product = cls.Product.create(
            {
                "name": "Product - Test",
                "type": "product",
                "list_price": 100.00,
                "standard_price": 100.00,
            }
        )
        cls.product2 = cls.Product.create(
            {
                "name": "Product2 - Test",
                "type": "product",
                "list_price": 100.00,
                "standard_price": 100.00,
            }
        )
        cls.customer = cls.env["res.partner"].create({"name": "Customer - test"})
        cls.picking_type = cls.PickingType.search(
            [("warehouse_id", "=", cls.warehouse.id), ("code", "=", "outgoing")]
        )
        cls.picking = cls.Picking.create(
            {
                "name": "picking - test 01",
                "location_id": cls.warehouse.lot_stock_id.id,
                "location_dest_id": cls.warehouse.wh_output_stock_loc_id.id,
                "picking_type_id": cls.picking_type.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.product_variant_ids.id,
                            "product_uom_qty": 20.0,
                            "product_uom": cls.product.uom_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product2.product_variant_ids.id,
                            "product_uom_qty": 60.0,
                            "product_uom": cls.product.uom_id.id,
                        },
                    ),
                ],
            }
        )

    def qty_on_hand(self, product):
        wiz = self.env["stock.inventory"].create(
            {
                "name": "Stock Inventory",
                "product_ids": [(4, product.id, 0)],
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_id": product.uom_id.id,
                            "product_qty": 200,
                            "location_id": self.warehouse.lot_stock_id.id,
                        },
                    ),
                ],
            }
        )
        wiz.action_start()
        wiz.action_validate()

    def test_stock_move_change_source_location_all(self):
        self.qty_on_hand(self.product.product_variant_ids)
        self.qty_on_hand(self.product2.product_variant_ids)
        self.picking.action_assign()
        new_location_id = self.Location.create(
            {"name": "Shelf 1", "location_id": self.warehouse.lot_stock_id.id}
        )
        wiz = self.Wizard.with_context(
            active_model=self.picking._name,
            active_ids=self.picking.ids,
        ).create({"new_location_id": new_location_id.id, "moves_to_change": "all"})
        move_lines = self.picking.mapped("move_lines")
        self.assertEqual(
            wiz.warehouse_view_location_id,
            self.picking.location_id.get_warehouse().view_location_id,
        )
        self.assertEqual(wiz.old_location_id, move_lines[:1].location_id)
        wiz.action_apply()
        move_lines = self.picking.mapped("move_lines.location_id")
        self.assertEqual(len(move_lines), 1)

    def test_stock_move_change_source_location_matched(self):
        self.qty_on_hand(self.product.product_variant_ids)
        self.qty_on_hand(self.product2.product_variant_ids)
        self.picking.action_assign()
        new_location_id = self.Location.create(
            {"name": "Shelf 1", "location_id": self.warehouse.lot_stock_id.id}
        )
        other_location_id = self.Location.create(
            {"name": "Shelf 2", "location_id": self.warehouse.lot_stock_id.id}
        )
        self.picking.action_assign()
        move_lines = self.picking.mapped("move_lines")
        move_lines[:1].write({"location_id": other_location_id.id})
        wiz = self.Wizard.with_context(
            active_model=self.picking._name,
            active_ids=self.picking.ids,
        ).create(
            {
                "old_location_id": self.picking.location_id.id,
                "new_location_id": new_location_id.id,
                "moves_to_change": "matched",
            }
        )
        wiz.action_apply()
        move_lines = self.picking.mapped("move_lines.location_id")
        self.assertEqual(len(move_lines), 2)

    def test_stock_move_change_source_location_manual(self):
        self.qty_on_hand(self.product.product_variant_ids)
        self.qty_on_hand(self.product2.product_variant_ids)
        self.picking.action_assign()
        new_location_id = self.Location.create(
            {"name": "Shelf 1", "location_id": self.warehouse.lot_stock_id.id}
        )
        wiz = self.Wizard.with_context(
            active_model=self.picking._name,
            active_ids=self.picking.ids,
        ).create(
            {
                "new_location_id": new_location_id.id,
                "moves_to_change": "manual",
                "move_lines": [(6, 0, self.picking.move_lines[0].ids)],
            }
        )
        move_lines = self.picking.mapped("move_lines")
        self.assertEqual(wiz.old_location_id, move_lines[:1].location_id)
        wiz.action_apply()
        move_lines = self.picking.mapped("move_lines.location_id")
        self.assertEqual(len(move_lines), 2)

    def test_stock_move_change_source_location_failed(self):
        self.qty_on_hand(self.product.product_variant_ids)
        self.qty_on_hand(self.product2.product_variant_ids)
        self.picking.action_assign()
        for move in self.picking.move_lines:
            move.quantity_done = 1
        self.picking._action_done()
        new_location_id = self.Location.create(
            {"name": "Shelf 1", "location_id": self.warehouse.lot_stock_id.id}
        )
        wiz = self.Wizard.with_context(
            active_model=self.picking._name,
            active_ids=self.picking.ids,
        ).create({"new_location_id": new_location_id.id, "moves_to_change": "all"})
        with self.assertRaises(UserError):
            wiz.action_apply()
