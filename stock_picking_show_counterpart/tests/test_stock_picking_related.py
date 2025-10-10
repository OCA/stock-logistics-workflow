from odoo.tests.common import TransactionCase


class TestStockPickingRelated(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.StockPicking = cls.env["stock.picking"]
        cls.StockMove = cls.env["stock.move"]
        cls.picking_type_internal = cls.env.ref("stock.picking_type_internal")
        cls.product = cls.env.ref("product.product_product_4")
        cls.wh1 = cls.env.ref("stock.warehouse0")
        cls.wh2 = cls.env["stock.warehouse"].create(
            {
                "name": "Warehouse 02",
                "code": "WH02",
            }
        )
        # Add available quantity of the product to WH1's stock location
        cls.env["stock.quant"]._update_available_quantity(
            cls.product,
            cls.wh1.lot_stock_id,
            5,
        )
        # Create picking1: transfer from WH1 to WH2
        cls.picking1 = cls.StockPicking.create(
            {
                "name": "PICK1",
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.wh2.lot_stock_id.id,
                "picking_type_id": cls.picking_type_internal.id,
            }
        )
        # Create picking2: reverse transfer from WH2 to WH1
        cls.picking2 = cls.StockPicking.create(
            {
                "name": "PICK2",
                "location_id": cls.wh2.lot_stock_id.id,
                "location_dest_id": cls.wh1.lot_stock_id.id,
                "picking_type_id": cls.picking_type_internal.id,
            }
        )
        # Create stock move for picking1 (WH1 -> WH2)
        cls.move1 = cls.StockMove.create(
            {
                "name": "Inter WH Move 1",
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 1,
                "location_id": cls.wh1.lot_stock_id.id,
                "location_dest_id": cls.wh2.lot_stock_id.id,
                "picking_id": cls.picking1.id,
            }
        )
        # Create stock move for picking2 (WH2 -> WH1), chained to move1
        cls.move2 = cls.StockMove.create(
            {
                "name": "Inter WH Move 2",
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 1,
                "location_id": cls.wh2.lot_stock_id.id,
                "location_dest_id": cls.wh1.lot_stock_id.id,
                "picking_id": cls.picking2.id,
                "move_orig_ids": [(6, 0, [cls.move1.id])],
            }
        )

        # Confirm & validate pickings
        cls.picking1.action_confirm()
        cls.picking2.action_confirm()

    def test_get_related_pickings(self):
        """
        Test that inter-warehouse pickings are correctly linked as related pickings.
        """
        # Check that picking1 sees picking2 as a related picking
        self.assertIn(
            self.picking2,
            self.picking1._get_related_pickings(),
            "Picking1 should have Picking2 as a related picking after workflow.",
        )

        # Check that picking2 sees picking1 as a related picking
        self.assertIn(
            self.picking1,
            self.picking2._get_related_pickings(),
            "Picking2 should have Picking1 as a related picking after workflow.",
        )

        # Check that related picking counts are updated correctly
        self.assertEqual(
            self.picking1.related_picking_count,
            1,
            "Picking1 should have 1 related picking automatically.",
        )
        self.assertEqual(
            self.picking2.related_picking_count,
            1,
            "Picking2 should have 1 related picking automatically.",
        )

    def test_action_view_related_pickings(self):
        """
        Test the returned action dictionary from the 'View Related Pickings' button.
        Ensures the correct model, action type, and domain are returned.
        """
        action = self.picking1.action_view_related_pickings()

        # Validate that the returned action is a window action on stock.picking
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "stock.picking")

        # Check that the related picking (picking2) is included in the domain filter
        self.assertIn(self.picking2.id, action["domain"][0][2])
