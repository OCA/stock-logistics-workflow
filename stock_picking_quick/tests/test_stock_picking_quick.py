from odoo.tests.common import TransactionCase


class TestStockPickingQuick(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Product = cls.env["product.product"]
        cls.Picking = cls.env["stock.picking"]
        cls.StockMove = cls.env["stock.move"]

        cls.company = cls.env.company
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.location_customer = cls.env.ref("stock.stock_location_customers")

        cls.product_1 = cls.Product.create(
            {
                "name": "Test Product 1",
                "type": "consu",
                "standard_price": 100.0,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )

        cls.product_2 = cls.Product.create(
            {
                "name": "Test Product 2",
                "type": "consu",
                "standard_price": 200.0,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )

        cls.picking = cls.Picking.create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.location_stock.id,
                "location_dest_id": cls.location_customer.id,
            }
        )

    def test_get_product_catalog_record_lines(self):
        """Existing stock moves are returned grouped by product."""
        move_1 = self.StockMove.create(
            {
                "name": self.product_1.display_name,
                "product_id": self.product_1.id,
                "product_uom_qty": 5.0,
                "product_uom": self.product_1.uom_id.id,
                "picking_id": self.picking.id,
                "location_id": self.picking.location_id.id,
                "location_dest_id": self.picking.location_dest_id.id,
            }
        )

        move_2 = self.StockMove.create(
            {
                "name": self.product_2.display_name,
                "product_id": self.product_2.id,
                "product_uom_qty": 10.0,
                "product_uom": self.product_2.uom_id.id,
                "picking_id": self.picking.id,
                "location_id": self.picking.location_id.id,
                "location_dest_id": self.picking.location_dest_id.id,
            }
        )

        result = self.picking._get_product_catalog_record_lines(
            [self.product_1.id, self.product_2.id]
        )

        self.assertIn(self.product_1, result)
        self.assertIn(self.product_2, result)

        self.assertEqual(result[self.product_1], move_1)
        self.assertEqual(result[self.product_2], move_2)

    def test_get_product_catalog_order_data(self):
        """Products without existing moves get their default price."""
        result = self.picking._get_product_catalog_order_data(
            self.product_1 | self.product_2
        )

        self.assertEqual(
            result[self.product_1.id]["price"],
            self.product_1.standard_price,
        )
        self.assertEqual(
            result[self.product_2.id]["price"],
            self.product_2.standard_price,
        )

    def test_get_product_catalog_lines_data(self):
        """Existing move data is correctly returned to the catalog."""
        move = self.StockMove.create(
            {
                "name": self.product_1.display_name,
                "product_id": self.product_1.id,
                "product_uom_qty": 7.0,
                "product_uom": self.product_1.uom_id.id,
                "picking_id": self.picking.id,
                "location_id": self.picking.location_id.id,
                "location_dest_id": self.picking.location_dest_id.id,
            }
        )

        result = move._get_product_catalog_lines_data(parent_record=self.picking)

        self.assertEqual(result["quantity"], 7.0)
        self.assertEqual(
            result["price"],
            self.product_1.standard_price,
        )

    def test_update_order_line_info_create_move(self):
        """Adding a product creates a stock move."""
        self.assertFalse(
            self.picking.move_ids_without_package.filtered(
                lambda move: move.product_id == self.product_1
            )
        )

        result = self.picking._update_order_line_info(
            self.product_1.id,
            5.0,
        )

        self.assertEqual(result, 5.0)

        move = self.picking.move_ids_without_package.filtered(
            lambda move: move.product_id == self.product_1
        )

        self.assertEqual(len(move), 1)
        self.assertEqual(move.product_uom_qty, 5.0)
        self.assertEqual(move.product_id, self.product_1)
        self.assertEqual(
            move.location_id,
            self.picking.location_id,
        )
        self.assertEqual(
            move.location_dest_id,
            self.picking.location_dest_id,
        )

    def test_update_order_line_info_update_move(self):
        """Updating an existing product changes the move quantity."""
        move = self.StockMove.create(
            {
                "name": self.product_1.display_name,
                "product_id": self.product_1.id,
                "product_uom_qty": 5.0,
                "product_uom": self.product_1.uom_id.id,
                "picking_id": self.picking.id,
                "location_id": self.picking.location_id.id,
                "location_dest_id": self.picking.location_dest_id.id,
            }
        )

        result = self.picking._update_order_line_info(
            self.product_1.id,
            12.0,
        )

        self.assertEqual(result, 12.0)
        self.assertEqual(move.product_uom_qty, 12.0)

        self.assertEqual(
            len(
                self.picking.move_ids_without_package.filtered(
                    lambda m: m.product_id == self.product_1
                )
            ),
            1,
        )

    def test_update_order_line_info_delete_move(self):
        """Setting quantity to zero removes the existing move."""
        move = self.StockMove.create(
            {
                "name": self.product_1.display_name,
                "product_id": self.product_1.id,
                "product_uom_qty": 5.0,
                "product_uom": self.product_1.uom_id.id,
                "picking_id": self.picking.id,
                "location_id": self.picking.location_id.id,
                "location_dest_id": self.picking.location_dest_id.id,
            }
        )

        self.picking._update_order_line_info(
            self.product_1.id,
            0,
        )

        self.assertFalse(move.exists())

    def test_update_order_line_info_ignore_negative_quantity(self):
        """A negative quantity does not create a move."""
        result = self.picking._update_order_line_info(
            self.product_1.id,
            -5.0,
        )

        self.assertEqual(result, 0)

        self.assertFalse(
            self.picking.move_ids_without_package.filtered(
                lambda move: move.product_id == self.product_1
            )
        )

    def test_action_add_from_catalog_picking(self):
        """The stock.move action uses the picking from the context."""
        move = self.StockMove.create(
            {
                "name": self.product_1.display_name,
                "product_id": self.product_1.id,
                "product_uom_qty": 5.0,
                "product_uom": self.product_1.uom_id.id,
                "picking_id": self.picking.id,
                "location_id": self.picking.location_id.id,
                "location_dest_id": self.picking.location_dest_id.id,
            }
        )

        action = move.with_context(
            picking_id=self.picking.id
        ).action_add_from_catalog_picking()

        self.assertEqual(action["type"], "ir.actions.act_window")

    def test_get_product_catalog_order_line_info(self):
        self.StockMove.create(
            {
                "name": self.product_1.display_name,
                "product_id": self.product_1.id,
                "product_uom_qty": 8.0,
                "product_uom": self.product_1.uom_id.id,
                "picking_id": self.picking.id,
                "location_id": self.picking.location_id.id,
                "location_dest_id": self.picking.location_dest_id.id,
            }
        )

        result = self.picking._get_product_catalog_order_line_info(
            [self.product_1.id, self.product_2.id],
            child_field="move_ids_without_package",
        )

        # Existing move
        self.assertEqual(
            result[self.product_1.id]["quantity"],
            8.0,
        )
        self.assertEqual(
            result[self.product_1.id]["price"],
            self.product_1.standard_price,
        )
        self.assertEqual(
            result[self.product_1.id]["productType"],
            self.product_1.type,
        )

        # Product without existing move
        self.assertEqual(
            result[self.product_2.id]["price"],
            self.product_2.standard_price,
        )

    def test_action_add_from_catalog_picking_without_picking(self):
        move = self.StockMove.create(
            {
                "name": self.product_1.display_name,
                "product_id": self.product_1.id,
                "product_uom_qty": 5.0,
                "product_uom": self.product_1.uom_id.id,
                "picking_id": self.picking.id,
                "location_id": self.picking.location_id.id,
                "location_dest_id": self.picking.location_dest_id.id,
            }
        )

        self.assertFalse(move.action_add_from_catalog_picking())
