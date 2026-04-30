# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockPickingOriginState(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.warehouse.delivery_steps = "pick_pack_ship"
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "product"}
        )
        cls.customer = cls.env["res.partner"].create({"name": "Test Customer"})

    def _create_three_step_delivery(self, qty=5.0, available_qty=None):
        """Create a 3-step delivery for the test product.

        Returns the (pick, pack, out) pickings recordset tuple.
        """
        if available_qty is None:
            available_qty = qty
        if available_qty:
            self.env["stock.quant"]._update_available_quantity(
                self.product, self.warehouse.lot_stock_id, available_qty
            )
        group = self.env["procurement.group"].create(
            {"name": "Test Delivery", "partner_id": self.customer.id}
        )
        self.env["procurement.group"].run(
            [
                group.Procurement(
                    self.product,
                    qty,
                    self.product.uom_id,
                    self.env.ref("stock.stock_location_customers"),
                    "Test Delivery",
                    "Test Delivery",
                    self.warehouse.company_id,
                    {"warehouse_id": self.warehouse, "group_id": group},
                )
            ]
        )
        pickings = self.env["stock.picking"].search(
            [("group_id", "=", group.id)], order="id"
        )
        out_picking = pickings.filtered(
            lambda p: p.picking_type_id == self.warehouse.out_type_id
        )
        pack_picking = pickings.filtered(
            lambda p: p.picking_type_id == self.warehouse.pack_type_id
        )
        pick_picking = pickings.filtered(
            lambda p: p.picking_type_id == self.warehouse.pick_type_id
        )
        return pick_picking, pack_picking, out_picking

    def _validate_picking(self, picking):
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
            move.picked = True
        picking._action_done()

    def test_01_no_origin(self):
        """A picking with no origin pickings has empty origin fields."""
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.in_type_id.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.warehouse.lot_stock_id.id,
            }
        )
        self.assertFalse(picking.origin_state)
        self.assertFalse(picking.origin_state_label)

    def test_02_three_step_pick_waiting(self):
        """When PICK has no reservation, OUT shows PICK as waiting."""
        pick, pack, out = self._create_three_step_delivery(available_qty=0)
        self.assertEqual(out.origin_state, "waiting")
        self.assertIn(self.warehouse.pick_type_id.display_name, out.origin_state_label)

    def test_03_three_step_pick_assigned(self):
        """When PICK is fully reserved, OUT shows PICK as assigned."""
        pick, pack, out = self._create_three_step_delivery()
        pick.action_assign()
        self.assertEqual(pick.state, "assigned")
        self.assertEqual(out.origin_state, "assigned")
        self.assertIn(self.warehouse.pick_type_id.display_name, out.origin_state_label)

    def test_04_three_step_pick_partial(self):
        """When PICK is partially reserved, OUT reports partially_available."""
        pick, pack, out = self._create_three_step_delivery(qty=10, available_qty=4)
        pick.action_assign()
        self.assertEqual(out.origin_state, "partially_available")
        self.assertIn(self.warehouse.pick_type_id.display_name, out.origin_state_label)

    def test_05_three_step_pick_done_pack_waiting(self):
        """Once PICK is done, OUT escalates to PACK."""
        pick, pack, out = self._create_three_step_delivery()
        pick.action_assign()
        self._validate_picking(pick)
        self.assertEqual(pick.state, "done")
        self.assertIn(self.warehouse.pack_type_id.display_name, out.origin_state_label)
        self.assertIn(out.origin_state, ("waiting", "assigned"))

    def test_06_three_step_all_origins_done(self):
        """Once both PICK and PACK are done, OUT reports the shallowest
        level (PACK) as done."""
        pick, pack, out = self._create_three_step_delivery()
        pick.action_assign()
        self._validate_picking(pick)
        pack.action_assign()
        self._validate_picking(pack)
        self.assertEqual(out.origin_state, "done")
        self.assertIn(self.warehouse.pack_type_id.display_name, out.origin_state_label)

    def test_07_multiple_pickings_worst_state_wins(self):
        """With several PICKs, the least-favorable state is reported."""
        pick1, pack1, out1 = self._create_three_step_delivery()
        pick2, pack2, out2 = self._create_three_step_delivery(available_qty=0)
        pick1.action_assign()
        self.assertEqual(pick1.state, "assigned")
        self.assertEqual(pick2.state, "confirmed")
        out1.move_ids.move_orig_ids.move_orig_ids |= pick2.move_ids
        out1.invalidate_recordset(["origin_state", "origin_state_label"])
        self.assertEqual(out1.origin_state, "waiting")
