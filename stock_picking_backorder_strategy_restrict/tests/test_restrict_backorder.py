from odoo.exceptions import ValidationError

from odoo.addons.stock.tests.common import TestStockCommon


class TestStockPickingBackorder(TestStockCommon):
    @classmethod
    def setUpClass(cls):
        """Configurations for Back-order Restriction."""
        super().setUpClass()

        # Copy existing picking_type_in with modifications
        picking_type_in = cls.env["stock.picking.type"].browse(cls.picking_type_in)
        cls.picking_type_restrict = picking_type_in.copy(
            {
                "sequence_code": "restrict",
                "create_backorder": "restrict",
            }
        )

        # Create a picking using the restrictive picking type
        cls.picking = cls.PickingObj.create(
            {
                "picking_type_id": cls.picking_type_restrict.id,
                "location_id": cls.supplier_location,
                "state": "draft",
                "location_dest_id": cls.stock_location,
            }
        )

        # Create a stock move with quantity 10
        cls.move = cls.MoveObj.create(
            {
                "name": cls.productA.name,
                "product_id": cls.productA.id,
                "product_uom_qty": 10,
                "product_uom": cls.productA.uom_id.id,
                "picking_id": cls.picking.id,
                "location_id": cls.supplier_location,
                "location_dest_id": cls.stock_location,
            }
        )

        # Confirm and assign
        cls.picking.action_confirm()

    def test_backorder_restricted_partial(self):
        """
        Test that a ValidationError is raised for partial delivery with
        back-orders restricted.
        """
        self.move.move_line_ids.quantity = 4
        with self.assertRaises(ValidationError):
            self.picking.button_validate()

    def test_backorder_restricted_full_delivery(self):
        """
        Test that no error is raised for full delivery with back-orders restricted.
        """
        self.move.move_line_ids.quantity = self.move.product_uom_qty
        self.picking.button_validate()
        self.assertEqual(
            self.picking.state,
            "done",
            "Picking should be fully delivered without backorder.",
        )
