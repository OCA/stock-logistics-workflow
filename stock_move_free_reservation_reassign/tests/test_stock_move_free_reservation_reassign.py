# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockMoveFreeReservationReassign(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {"name": "Product A", "type": "product"}
        )
        cls.location_1 = cls.env["stock.location"].create(
            {
                "name": "Location 1",
                "usage": "internal",
                "location_id": cls.stock_location.id,
            }
        )
        cls.location_2 = cls.env["stock.location"].create(
            {
                "name": "Location 2",
                "usage": "internal",
                "location_id": cls.stock_location.id,
            }
        )
        cls.pick_type_out = cls.env.ref("stock.picking_type_out")
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls._set_qty_in_location(cls.product, cls.location_1, 10.0)
        cls._set_qty_in_location(cls.product, cls.location_2, 10.0)

    @classmethod
    def _set_qty_in_location(cls, product, location, quantity):
        """Set the quantity of a product in a location"""
        cls.env["stock.quant"]._update_available_quantity(product, location, quantity)

    @classmethod
    def _make_location_inventory(cls, product, location, quantity: float):
        """Make an inventory for the given product in the given location"""
        inventory_quant = (
            cls.env["stock.quant"]
            .with_context(inventory_mode=True)
            .create(
                {
                    "location_id": location.id,
                    "product_id": product.id,
                    "inventory_quantity": quantity,
                }
            )
        )
        inventory_quant.action_apply_inventory()

    @classmethod
    def _create_move_picking_out(cls, product, quantity: float):
        return (
            cls.env["stock.move"]
            .create(
                {
                    "name": "Move",
                    "product_id": product.id,
                    "product_uom_qty": quantity,
                    "product_uom": product.uom_id.id,
                    "location_id": cls.stock_location.id,
                    "location_dest_id": cls.customer_location.id,
                    "picking_type_id": cls.pick_type_out.id,
                    "partner_id": cls.partner.id,
                }
            )
            ._action_confirm()
        )

    def test_auto_assign(self):
        self.env["res.config.settings"].create(
            {"reassign_stock_move_after_free_reservation": True}
        ).execute()
        self.assertEqual(self.product.qty_available, 20.0)
        move = self._create_move_picking_out(self.product, 10.0)
        move._action_assign()
        self.assertEqual(move.state, "assigned")
        self.assertEqual(len(move.move_line_ids), 1)
        # make an inventory on the reserved location
        initial_location = move.move_line_ids.location_id
        self._make_location_inventory(self.product, initial_location, 0)
        self.assertEqual(self.product.qty_available, 10.0)
        # the move should still be assigned but a new move should be created
        self.assertEqual(move.state, "assigned")
        self.assertEqual(len(move.move_line_ids), 1)
        self.assertNotEqual(move.move_line_ids.location_id, initial_location)

    def test_no_auto_reassign(self):
        # by default reassign is disabled
        self.assertEqual(self.product.qty_available, 20.0)
        move = self._create_move_picking_out(self.product, 10.0)
        move._action_assign()
        self.assertEqual(move.state, "assigned")
        # make an inventory on the reserved location
        initial_location = move.move_line_ids.location_id
        self._make_location_inventory(self.product, initial_location, 0)
        self.assertEqual(self.product.qty_available, 10.0)
        # the move should still be assigned but a new move should be created
        self.assertEqual(move.state, "confirmed")
