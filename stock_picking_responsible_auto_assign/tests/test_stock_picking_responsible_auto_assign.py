# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestStockPickingResponsibleAutoAssign(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.pack_location = cls.env["stock.location"].create(
            {"name": "Packing Zone", "location_id": cls.stock_location.id}
        )
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        group = cls.env.ref("stock.group_stock_user")
        cls.picker_a, cls.picker_b, cls.packer_c, cls.packer_d = (
            cls.env["res.users"].create(
                {
                    "name": name,
                    "login": name.lower(),
                    "group_ids": [Command.link(group.id)],
                }
            )
            for name in ("Picker A", "Picker B", "Packer C", "Packer D")
        )
        cls.pick_type = cls.env["stock.picking.type"].create(
            {
                "name": "Pick",
                "code": "internal",
                "sequence_code": "TPICK",
                "warehouse_id": cls.warehouse.id,
                "default_location_src_id": cls.stock_location.id,
                "default_location_dest_id": cls.pack_location.id,
                "reservation_method": "manual",
                "responsible_assign_mode": "ready",
                "responsible_user_ids": [
                    Command.set((cls.picker_a | cls.picker_b).ids)
                ],
            }
        )
        cls.pack_type = cls.env["stock.picking.type"].create(
            {
                "name": "Pack",
                "code": "outgoing",
                "sequence_code": "TPACK",
                "warehouse_id": cls.warehouse.id,
                "default_location_src_id": cls.pack_location.id,
                "default_location_dest_id": cls.customer_location.id,
                "responsible_assign_mode": "previous",
                "responsible_user_ids": [
                    Command.set((cls.packer_c | cls.packer_d).ids)
                ],
            }
        )
        cls.products = cls.env["product.product"].create(
            [{"name": f"Product {i}", "is_storable": True} for i in range(60)]
        )
        for product in cls.products:
            cls.env["stock.quant"]._update_available_quantity(
                product, cls.stock_location, 1000
            )

    def _create_picking(self, picking_type, lines, orig_moves=None, qty=1):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "location_id": picking_type.default_location_src_id.id,
                            "location_dest_id": (
                                picking_type.default_location_dest_id.id
                            ),
                        }
                    )
                    for product in self.products[:lines]
                ],
            }
        )
        if orig_moves:
            for move, orig in zip(picking.move_ids, orig_moves, strict=True):
                move.move_orig_ids = orig
        picking.action_confirm()
        return picking

    def _create_chain(self, lines, qty=1):
        """A pick ready to be reserved, chained to a waiting pack."""
        pick = self._create_picking(self.pick_type, lines, qty=qty)
        pack = self._create_picking(
            self.pack_type, lines, orig_moves=pick.move_ids, qty=qty
        )
        self.assertEqual(pack.state, "waiting")
        return pick, pack

    def test_01_least_loaded_by_lines(self):
        big, _ = self._create_chain(60)
        small_1, _ = self._create_chain(2)
        small_2, _ = self._create_chain(2)
        big.action_assign()
        self.assertEqual(big.user_id, self.picker_a)
        small_1.action_assign()
        self.assertEqual(small_1.user_id, self.picker_b)
        small_2.action_assign()
        # B has 2 lines pending, A has 60: B gets it again
        self.assertEqual(small_2.user_id, self.picker_b)

    def test_02_unavailable_user_is_skipped(self):
        self.picker_a.picking_assign_available = False
        for _i in range(3):
            pick, _ = self._create_chain(1)
            pick.action_assign()
            self.assertEqual(pick.user_id, self.picker_b)

    def test_03_manual_choice_in_pool_is_kept(self):
        pick, _ = self._create_chain(1)
        # created by the admin (default responsible), who is not in the pool
        self.assertEqual(pick.user_id, self.env.user)
        pick.user_id = self.picker_b
        pick.action_assign()
        self.assertEqual(pick.user_id, self.picker_b)
        # repeated reservations do not reshuffle
        pick.action_assign()
        self.assertEqual(pick.user_id, self.picker_b)

    def test_04_backorder_is_assigned(self):
        pick, _ = self._create_chain(1, qty=10)
        pick.action_assign()
        self.assertEqual(pick.user_id, self.picker_a)
        pick.move_ids.quantity = 4
        pick.move_ids.picked = True
        pick.with_context(skip_backorder=True).button_validate()
        backorder = pick.backorder_ids
        self.assertFalse(backorder.user_id)
        backorder.action_assign()
        self.assertEqual(backorder.state, "assigned")
        # A has nothing pending anymore (the pick is done), so A gets it
        self.assertEqual(backorder.user_id, self.picker_a)

    def test_05_chained_pack_balanced_in_its_pool(self):
        pick_1, pack_1 = self._create_chain(60)
        pick_2, pack_2 = self._create_chain(2)
        pick_1.action_assign()
        self.assertEqual(pack_1.user_id, self.packer_c)
        self.assertEqual(pick_1.next_picking_user_id, self.packer_c)
        pick_2.action_assign()
        self.assertEqual(pack_2.user_id, self.packer_d)
        self.assertEqual(pick_2.next_picking_user_id, self.packer_d)

    def test_06_chained_pack_same_user(self):
        self.pack_type.responsible_assign_same_user = True
        pick, pack = self._create_chain(3)
        pick.action_assign()
        self.assertEqual(pack.user_id, pick.user_id)

    def test_07_chain_three_levels(self):
        ship_type = self.pack_type.copy(
            {
                "name": "Ship",
                "sequence_code": "TSHIP",
                "responsible_assign_same_user": True,
            }
        )
        pick, pack = self._create_chain(2)
        ship = self._create_picking(ship_type, 2, orig_moves=pack.move_ids)
        pick.action_assign()
        self.assertEqual(pack.user_id, self.packer_c)
        self.assertEqual(ship.user_id, self.packer_c)

    def test_08_manual_mode_does_nothing(self):
        self.pick_type.responsible_assign_mode = "manual"
        pick, pack = self._create_chain(1)
        pick.action_assign()
        self.assertEqual(pick.user_id, self.env.user)
        self.assertEqual(pack.user_id, self.env.user)

    def test_09_reassign_forces_least_loaded(self):
        pick_1, _ = self._create_chain(60)
        pick_2, _ = self._create_chain(2)
        pick_1.action_assign()
        pick_2.action_assign()
        self.assertEqual(pick_2.user_id, self.picker_b)
        self.picker_b.picking_assign_available = False
        pick_2.action_auto_assign_responsible()
        self.assertEqual(pick_2.user_id, self.picker_a)

    def test_10_load_measures(self):
        self.pick_type.responsible_assign_load = "quantity"
        pick_1, _ = self._create_chain(1, qty=100)
        pick_2, _ = self._create_chain(5, qty=1)
        pick_3, _ = self._create_chain(1, qty=1)
        pick_1.action_assign()
        pick_2.action_assign()
        pick_3.action_assign()
        # A: 100 units, B: 5 units -> B gets the third one
        self.assertEqual(pick_1.user_id, self.picker_a)
        self.assertEqual(pick_2.user_id, self.picker_b)
        self.assertEqual(pick_3.user_id, self.picker_b)

        self.pick_type.responsible_assign_load = "pickings"
        pick_4, _ = self._create_chain(1)
        pick_4.action_assign()
        # A: 1 transfer, B: 2 transfers -> A
        self.assertEqual(pick_4.user_id, self.picker_a)

    def test_11_pack_confirmed_after_pick_is_assigned(self):
        pick = self._create_picking(self.pick_type, 2)
        pick.action_assign()
        self.assertEqual(pick.user_id, self.picker_a)
        pack = self._create_picking(self.pack_type, 2, orig_moves=pick.move_ids)
        self.assertEqual(pack.user_id, self.packer_c)
        self.assertEqual(pick.next_picking_user_id, self.packer_c)

    def test_12_no_pool_does_nothing(self):
        self.pick_type.responsible_user_ids = False
        pick, _ = self._create_chain(1)
        pick.action_assign()
        self.assertEqual(pick.user_id, self.env.user)

    def _validate(self, picking):
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
        picking.move_ids.picked = True
        picking.button_validate()

    def test_13_queue_one_at_a_time(self):
        self.pick_type.responsible_assign_max_pending = 1
        pick_1, pack_1 = self._create_chain(60)
        pick_2, _ = self._create_chain(2)
        pick_3, pack_3 = self._create_chain(2)
        pick_4, _ = self._create_chain(2, qty=1)
        pick_4.priority = "1"
        for pick in (pick_1, pick_2, pick_3, pick_4):
            pick.action_assign()
        self.assertEqual(pick_1.user_id, self.picker_a)
        self.assertEqual(pick_2.user_id, self.picker_b)
        # both at their maximum: the rest wait unassigned, pack too
        self.assertFalse(pick_3.user_id)
        self.assertFalse(pick_4.user_id)
        self.assertEqual(pack_1.user_id, self.packer_c)
        self.assertNotIn(pack_3.user_id, self.packer_c | self.packer_d)
        # repeated reservation does not assign either
        pick_3.action_assign()
        self.assertFalse(pick_3.user_id)
        # B finishes: the urgent one goes to B, with its pack
        self._validate(pick_2)
        self.assertEqual(pick_4.user_id, self.picker_b)
        self.assertFalse(pick_3.user_id)
        self._validate(pick_4)
        self.assertEqual(pick_3.user_id, self.picker_b)
        self.assertEqual(pack_3.user_id, self.packer_d)

    def test_14_queue_cancel_and_availability(self):
        self.pick_type.responsible_assign_max_pending = 1
        self.picker_b.picking_assign_available = False
        pick_1, _ = self._create_chain(1)
        pick_2, _ = self._create_chain(1)
        (pick_1 | pick_2).action_assign()
        self.assertEqual(pick_1.user_id, self.picker_a)
        self.assertFalse(pick_2.user_id)
        self.picker_b.picking_assign_available = True
        self.assertEqual(pick_2.user_id, self.picker_b)
        pick_3, _ = self._create_chain(1)
        pick_3.action_assign()
        self.assertFalse(pick_3.user_id)
        pick_1.action_cancel()
        self.assertEqual(pick_3.user_id, self.picker_a)

    def test_15_no_limit_assigns_everything(self):
        picks = [self._create_chain(1)[0] for _ in range(4)]
        for pick in picks:
            pick.action_assign()
        self.assertTrue(all(p.user_id in self.picker_a | self.picker_b for p in picks))

    def test_16_next_responsible_editable(self):
        pick, pack = self._create_chain(2)
        pick.action_assign()
        self.assertEqual(pick.next_picking_id, pack)
        self.assertEqual(pick.next_picking_user_id, self.packer_c)
        pick.next_picking_user_id = self.packer_d
        self.assertEqual(pack.user_id, self.packer_d)
        pack.user_id = self.packer_c
        self.assertEqual(pick.next_picking_user_id, self.packer_c)
        self._validate(pick)
        self._validate(pack)
        self.assertFalse(pick.next_picking_id)

    def test_17_progress_and_in_progress(self):
        pick, _ = self._create_chain(3)
        self.assertEqual(pick.picking_progress, "0/3")
        self.assertFalse(pick.is_in_progress)
        pick.action_assign()
        self.assertEqual(pick.user_id, self.picker_a)
        line = pick.move_line_ids[0]
        line.quantity = line.quantity
        line.picked = True
        self.assertEqual(pick.picking_progress, "1/3")
        self.assertTrue(pick.is_in_progress)
        self.assertIn(
            pick, self.env["stock.picking"].search([("is_in_progress", "=", True)])
        )
        self.assertNotIn(
            pick, self.env["stock.picking"].search([("is_in_progress", "=", False)])
        )
        # reassign skips it, and complains when there is nothing else to do
        other, _ = self._create_chain(1)
        other.action_assign()
        self.assertEqual(other.user_id, self.picker_b)
        self.picker_b.picking_assign_available = False
        (pick | other).action_auto_assign_responsible()
        self.assertEqual(pick.user_id, self.picker_a)
        self.assertEqual(other.user_id, self.picker_a)
        with self.assertRaises(UserError):
            pick.action_auto_assign_responsible()
        self._validate(pick)
        self.assertFalse(pick.is_in_progress)
