# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from lxml import etree

from odoo.tools.sql import column_exists, create_column

from odoo.addons.stock.tests.common import TestStockCommon

from ..hooks import pre_init_hook, uninstall_hook


class TestPickingBatchPlanner(TestStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a warehouse with 2 steps using old rules setup.
        cls.warehouse_2_steps = cls.env["stock.warehouse"].create(
            {
                "name": "Warehouse 2 steps",
                "code": "2S",
                "reception_steps": "two_steps",
                "delivery_steps": "pick_ship",
            }
        )
        delivery_route_2 = cls.warehouse_2_steps.delivery_route_id
        delivery_route_2.rule_ids[0].write(
            {
                "location_dest_id": delivery_route_2.rule_ids[1].location_src_id.id,
                "name": "2S: Stock → Output",
            }
        )
        delivery_route_2.rule_ids[1].write({"action": "pull"})
        cls.pick_type = cls.warehouse_2_steps.pick_type_id
        cls.pick_type.write(
            {
                "auto_batch": False,
                "plan_batch": False,
                "batch_group_by_partner": False,
                "wave_group_by_product": False,
            }
        )
        cls.delivery_type = cls.warehouse_2_steps.out_type_id
        cls.delivery_type.write(
            {
                "auto_batch": True,
                "batch_group_by_partner": True,
            }
        )
        cls.partner_1 = cls.env["res.partner"].create(
            {
                "name": "Test Partner 1",
            }
        )
        cls.partner_2 = cls.env["res.partner"].create(
            {
                "name": "Test Partner 2",
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.productA, cls.warehouse_2_steps.lot_stock_id, 100
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.productB, cls.warehouse_2_steps.lot_stock_id, 100
        )

    def _create_picking(self, operation_type, from_loc, to_loc, partner):
        """Create a picking with two moves of different products"""
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": operation_type.id,
                "location_id": from_loc.id,
                "location_dest_id": to_loc.id,
                "state": "draft",
                "partner_id": partner.id,
            }
        )
        move_A, move_B = self.env["stock.move"].create(
            [
                {
                    "name": self.productA.name,
                    "product_id": self.productA.id,
                    "product_uom_qty": 1,
                    "product_uom": self.productA.uom_id.id,
                    "picking_id": picking.id,
                    "location_id": from_loc.id,
                    "location_dest_id": to_loc.id,
                },
                {
                    "name": self.productB.name,
                    "product_id": self.productB.id,
                    "product_uom_qty": 1,
                    "product_uom": self.productB.uom_id.id,
                    "picking_id": picking.id,
                    "location_id": from_loc.id,
                    "location_dest_id": to_loc.id,
                },
            ]
        )
        picking.action_confirm()
        picking.action_assign()
        return picking, move_A, move_B

    @staticmethod
    def _update_dest_moves(move_pick, move_delivery):
        """Link the picking moves as destination moves of the delivery moves"""
        move_pick.write({"move_dest_ids": [(4, move_delivery.id)]})

    def test_operation_type_view_get(self):
        """Check if field not planning is in the condition of attrib invisible for some
        fields"""
        fields = ["batch_max_lines", "batch_max_pickings", "batch_auto_confirm"]
        for field in fields:
            if node := etree.XML(self.delivery_type.get_view()["arch"]).xpath(
                f"//field[@name='{field}']"
            ):
                self.assertEqual(
                    node[0].attrib["invisible"], "not plan_batch and (not auto_batch)"
                )

    def test_stock_picking_plan_batches(self):
        """Check flow to create batches in origin pickings from batch"""
        # Set plan_batch with Wave criteria
        self.pick_type.write(
            {
                "auto_batch": False,
                "plan_batch": True,
                "batch_group_by_partner": True,
                "wave_group_by_product": False,
            }
        )
        # Sale 1 - Partner 1
        pick_1, move_pick_A, move_pick_B = self._create_picking(
            self.pick_type,
            self.pick_type.default_location_src_id,
            self.pick_type.default_location_dest_id,
            self.partner_1,
        )
        delivery_1, move_delivery_A, move_delivery_B = self._create_picking(
            self.delivery_type,
            self.delivery_type.default_location_src_id,
            self.delivery_type.default_location_dest_id,
            self.partner_1,
        )
        self._update_dest_moves(move_pick_A, move_delivery_A)
        self._update_dest_moves(move_pick_B, move_delivery_B)
        # Sale 2 - Partner 1
        pick_2, move_pick_A, move_pick_B = self._create_picking(
            self.pick_type,
            self.pick_type.default_location_src_id,
            self.pick_type.default_location_dest_id,
            self.partner_1,
        )
        delivery_2, move_delivery_A, move_delivery_B = self._create_picking(
            self.delivery_type,
            self.delivery_type.default_location_src_id,
            self.delivery_type.default_location_dest_id,
            self.partner_1,
        )
        self._update_dest_moves(move_pick_A, move_delivery_A)
        self._update_dest_moves(move_pick_B, move_delivery_B)
        # Sale 3 - Partner 2
        pick_3, move_pick_A, move_pick_B = self._create_picking(
            self.pick_type,
            self.pick_type.default_location_src_id,
            self.pick_type.default_location_dest_id,
            self.partner_2,
        )
        delivery_3, move_delivery_A, move_delivery_B = self._create_picking(
            self.delivery_type,
            self.delivery_type.default_location_src_id,
            self.delivery_type.default_location_dest_id,
            self.partner_2,
        )
        self._update_dest_moves(move_pick_A, move_delivery_A)
        self._update_dest_moves(move_pick_B, move_delivery_B)
        # Sale 4 - Partner 2
        pick_4, move_pick_A, move_pick_B = self._create_picking(
            self.pick_type,
            self.pick_type.default_location_src_id,
            self.pick_type.default_location_dest_id,
            self.partner_2,
        )
        delivery_4, move_delivery_A, move_delivery_B = self._create_picking(
            self.delivery_type,
            self.delivery_type.default_location_src_id,
            self.delivery_type.default_location_dest_id,
            self.partner_2,
        )
        self._update_dest_moves(move_pick_A, move_delivery_A)
        self._update_dest_moves(move_pick_B, move_delivery_B)
        # All pickings and origin pickings
        all_orig_pickings = pick_1 | pick_2 | pick_3 | pick_4
        all_pickings = delivery_1 | delivery_2 | delivery_3 | delivery_4
        # Common batch
        batch = self.env["stock.picking.batch"].create(
            {
                "picking_ids": [(6, 0, all_pickings.ids)],
            }
        )
        batch.action_confirm()
        self.assertTrue(batch.can_plan_batches)
        batch.action_plan_batches()
        # Generated batches
        orig_batches = all_pickings.move_ids.move_orig_ids.picking_id.batch_id
        self.assertEqual(len(orig_batches), 2)
        self.assertEqual(batch.origin_batches_count, 2)
        all_pick_check = self.env["stock.picking"].browse()
        for orig_batch in orig_batches:
            self.assertEqual(len(orig_batch.picking_ids), 2)
            all_pick_check |= orig_batch.picking_ids
        self.assertEqual(all_pick_check, all_orig_pickings)
        for orig_picking in all_orig_pickings:
            self.assertTrue(orig_picking.batch_id)
        # Batch by partner, so Batches should be [(pick_1, pick_2), (pick_3, pick_4)]
        self.assertNotEqual(pick_1.batch_id, pick_3.batch_id)
        self.assertNotEqual(pick_2.batch_id, pick_4.batch_id)
        self.assertEqual(pick_1.batch_id, pick_2.batch_id)
        self.assertEqual(pick_3.batch_id, pick_4.batch_id)
        # Should create batches
        self.assertFalse(pick_1.batch_id.is_wave)
        self.assertFalse(pick_3.batch_id.is_wave)

    def test_stock_picking_plan_waves(self):
        """Check flow to create waves in origin pickings from batch"""
        # Set plan_batch with Wave criteria
        self.pick_type.write(
            {
                "auto_batch": False,
                "plan_batch": True,
                "batch_group_by_partner": False,
                "wave_group_by_product": True,
            }
        )
        # Sale 1 - Partner 1
        pick_1, move_pick_A, move_pick_B = self._create_picking(
            self.pick_type,
            self.pick_type.default_location_src_id,
            self.pick_type.default_location_dest_id,
            self.partner_1,
        )
        delivery_1, move_delivery_A, move_delivery_B = self._create_picking(
            self.delivery_type,
            self.delivery_type.default_location_src_id,
            self.delivery_type.default_location_dest_id,
            self.partner_1,
        )
        self._update_dest_moves(move_pick_A, move_delivery_A)
        self._update_dest_moves(move_pick_B, move_delivery_B)
        # Sale 2 - Partner 2
        pick_2, move_pick_A, move_pick_B = self._create_picking(
            self.pick_type,
            self.pick_type.default_location_src_id,
            self.pick_type.default_location_dest_id,
            self.partner_2,
        )
        delivery_2, move_delivery_A, move_delivery_B = self._create_picking(
            self.delivery_type,
            self.delivery_type.default_location_src_id,
            self.delivery_type.default_location_dest_id,
            self.partner_2,
        )
        self._update_dest_moves(move_pick_A, move_delivery_A)
        self._update_dest_moves(move_pick_B, move_delivery_B)
        # Common batch
        batch = self.env["stock.picking.batch"].create(
            {
                "picking_ids": [(6, 0, (delivery_1 | delivery_2).ids)],
            }
        )
        batch.action_confirm()
        self.assertTrue(batch.can_plan_batches)
        batch.action_plan_batches()
        self.assertTrue(pick_1.batch_id)
        self.assertTrue(pick_2.batch_id)
        # Wave by product, so pick_1 and pick_2 must be in the same wave
        self.assertEqual(pick_1.batch_id, pick_2.batch_id)
        # Should create a wave
        self.assertTrue(pick_1.batch_id.is_wave)
        self.assertEqual(batch.origin_batches_count, 2)

    def test_stock_picking_no_plan(self):
        """Check flow to check batch cannot create batches"""
        # Set plan_batch with Wave criteria
        self.pick_type.write(
            {
                "auto_batch": False,
                "plan_batch": False,
                "batch_group_by_partner": False,
                "wave_group_by_product": False,
            }
        )
        # Sale 1 - Partner 1
        pick_1, move_pick_A, move_pick_B = self._create_picking(
            self.pick_type,
            self.pick_type.default_location_src_id,
            self.pick_type.default_location_dest_id,
            self.partner_1,
        )
        delivery_1, move_delivery_A, move_delivery_B = self._create_picking(
            self.delivery_type,
            self.delivery_type.default_location_src_id,
            self.delivery_type.default_location_dest_id,
            self.partner_1,
        )
        self._update_dest_moves(move_pick_A, move_delivery_A)
        self._update_dest_moves(move_pick_B, move_delivery_B)
        # Sale 2 - Partner 2
        pick_2, move_pick_A, move_pick_B = self._create_picking(
            self.pick_type,
            self.pick_type.default_location_src_id,
            self.pick_type.default_location_dest_id,
            self.partner_2,
        )
        delivery_2, move_delivery_A, move_delivery_B = self._create_picking(
            self.delivery_type,
            self.delivery_type.default_location_src_id,
            self.delivery_type.default_location_dest_id,
            self.partner_2,
        )
        self._update_dest_moves(move_pick_A, move_delivery_A)
        self._update_dest_moves(move_pick_B, move_delivery_B)
        # Common batch
        batch = self.env["stock.picking.batch"].create(
            {
                "picking_ids": [(6, 0, (delivery_1 | delivery_2).ids)],
            }
        )
        batch.action_confirm()
        self.assertFalse(batch.can_plan_batches)

    def test_auto_batch_field(self):
        """Check the auto_batch field behavior"""
        # Respect user True value behavior
        self.pick_type.write(
            {
                "auto_batch": True,
                "plan_batch": True,
                "batch_group_by_partner": True,
            }
        )
        self.assertTrue(self.pick_type.auto_batch)
        self.assertTrue(self.pick_type.auto_batch_original)
        # Respect user False value behavior
        self.pick_type.write(
            {
                "auto_batch": False,
                "plan_batch": False,
                "batch_group_by_partner": False,
            }
        )
        self.assertFalse(self.pick_type.auto_batch)
        self.assertFalse(self.pick_type.auto_batch_original)
        # Behavior with plan_batch in context
        self.assertTrue(self.pick_type.with_context(plan_batch=True).auto_batch)
        self.assertFalse(self.pick_type.auto_batch)
        self.assertFalse(self.pick_type.auto_batch_original)

    def test_pre_init_hook(self):
        """Test the pre_init_hook creates the columns and copies the values"""
        # Create auto_batch column and set some values
        cr = self.env.cr
        if not column_exists(cr, "stock_picking_type", "auto_batch"):
            create_column(cr, "stock_picking_type", "auto_batch", "boolean")
        cr.execute(
            "UPDATE stock_picking_type SET auto_batch = TRUE WHERE id = %s",
            (self.pick_type.id,),
        )
        # Drop auto_batch_original and plan_batch columns if they exist
        if column_exists(cr, "stock_picking_type", "auto_batch_original"):
            cr.execute("ALTER TABLE stock_picking_type DROP COLUMN auto_batch_original")
        if column_exists(cr, "stock_picking_type", "plan_batch"):
            cr.execute("ALTER TABLE stock_picking_type DROP COLUMN plan_batch")
        # Ensure columns do not exist
        self.assertFalse(column_exists(cr, "stock_picking_type", "auto_batch_original"))
        self.assertFalse(column_exists(cr, "stock_picking_type", "plan_batch"))
        # Run pre_init_hook
        pre_init_hook(self.env)
        # Check columns now exist
        self.assertTrue(column_exists(cr, "stock_picking_type", "auto_batch_original"))
        self.assertTrue(column_exists(cr, "stock_picking_type", "plan_batch"))
        # Check values have been copied correctly
        cr.execute(
            """SELECT auto_batch, auto_batch_original, plan_batch
            FROM stock_picking_type WHERE id = %s""",
            (self.pick_type.id,),
        )
        for auto_batch, auto_batch_original, plan_batch in cr.fetchall():
            self.assertEqual(auto_batch, auto_batch_original)
            self.assertEqual(auto_batch, plan_batch)

    def test_uninstall_hook(self):
        """Test the uninstall_hook restores the auto_batch values"""
        cr = self.env.cr
        # Set auto_batch_original to True
        cr.execute(
            "UPDATE stock_picking_type SET auto_batch_original = TRUE WHERE id = %s",
            (self.pick_type.id,),
        )
        uninstall_hook(self.env)
        # Check auto_batch column now exists
        self.assertTrue(column_exists(cr, "stock_picking_type", "auto_batch"))
        # Check values have been restored correctly
        cr.execute(
            "SELECT auto_batch FROM stock_picking_type WHERE id = %s",
            (self.pick_type.id,),
        )
        for auto_batch in cr.fetchall():
            self.assertTrue(auto_batch)
