# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import TransactionCase


class TestPickingBatchPartnerEnable(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "allow_batch_grouping": True,
            }
        )
        # Set up a product with stock availability
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product A",
                "is_storable": True,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.stock_location, 1000
        )
        # Enable auto_batch on picking type
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.picking_type.write(
            {
                "auto_batch": True,
                "batch_group_by_partner": True,
            }
        )

    @classmethod
    def _create_picking(cls, partner):
        """Helper to create a picking with moves"""
        return cls.env["stock.picking"].create(
            {
                "partner_id": partner.id if partner else False,
                "picking_type_id": cls.picking_type.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 10,
                            "product_uom": cls.product.uom_id.id,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        }
                    )
                ],
            }
        )

    def test_allow_partner_batch_grouping_is_propagated(self):
        """Test that the allow_batch_grouping field is propagated to the children"""
        # Test that the child inherits from the parent
        child = self.partner.create(
            {
                "name": "Child Partner",
                "parent_id": self.partner.id,
            }
        )
        self.assertTrue(child.allow_batch_grouping)
        # Test that it's propagated when changed
        self.partner.allow_batch_grouping = False
        self.assertFalse(child.allow_batch_grouping)

    def test_excluded_partner_no_auto_batch(self):
        """Test that pickings for excluded partners are not auto-batched"""
        # Set partner to excluded
        self.partner.allow_batch_grouping = False

        # Create and process picking
        picking = self._create_picking(self.partner)
        picking.action_confirm()
        picking.action_assign()

        # Picking should not be in any batch
        self.assertFalse(picking.batch_id)

    def test_allowed_partner_auto_batched(self):
        """Test that pickings for allowed partners are auto-batched"""
        # Ensure partner is allowed
        self.partner.allow_batch_grouping = True

        # Create and process picking
        picking = self._create_picking(self.partner)
        picking.action_confirm()
        picking.action_assign()

        # Picking should be in a batch
        self.assertTrue(picking.batch_id)

    def test_mixed_partner_settings(self):
        """Test multiple pickings with one partner excluded and another allowed"""
        # Set partners: one excluded, one allowed
        other_partner = self.partner.copy(
            {
                "name": "Other Partner",
                "allow_batch_grouping": False,
            }
        )

        # Create pickings
        picking_excluded = self._create_picking(other_partner)
        picking_allowed_1 = self._create_picking(self.partner)
        picking_allowed_2 = self._create_picking(self.partner)

        # Confirm all pickings
        all_pickings = picking_excluded | picking_allowed_1 | picking_allowed_2
        all_pickings.action_confirm()
        all_pickings.action_assign()

        # Check that only the allowed pickings are batched
        self.assertTrue(picking_allowed_1.batch_id)
        self.assertTrue(picking_allowed_2.batch_id)
        self.assertFalse(picking_excluded.batch_id)
        self.assertEqual(picking_allowed_1.batch_id, picking_allowed_2.batch_id)

    def test_picking_without_partner_auto_batched(self):
        """Test that pickings without partner are still auto-batched"""
        # Create picking without partner
        picking = self._create_picking(None)
        picking.action_confirm()
        picking.action_assign()

        # Picking should be in a batch
        self.assertTrue(picking.batch_id)
