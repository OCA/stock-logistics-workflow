# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from .common import Common


class TestStockPickingForceAvailability(Common):
    def test_button_force_availability(self):
        # Call the button from a reserved transfer => No action returned
        res = self.picking_assigned.button_force_availability()
        self.assertEqual(res, True)
        # Call the button from a non-reserved transfer => Wizard action returned
        res = self.picking_confirmed.button_force_availability()
        self.assertEqual(res["active_id"], self.picking_confirmed.id)
        self.assertEqual(res["active_model"], self.picking_confirmed._name)

    def test_force_availability(self):
        # Unreserve the assigned transfer to reserve goods on the confirmed one
        wiz = self.get_force_availability_wizard(self.picking_confirmed)
        self.assertEqual(wiz.move_to_unreserve_ids, self.picking_assigned.move_lines)
        wiz.validate()
        self.assertEqual(self.picking_assigned.state, "confirmed")
        self.assertEqual(self.picking_confirmed.state, "assigned")
        # Reverse the operation
        wiz = self.get_force_availability_wizard(self.picking_assigned)
        self.assertEqual(wiz.move_to_unreserve_ids, self.picking_confirmed.move_lines)
        wiz.validate()
        self.assertEqual(self.picking_assigned.state, "assigned")
        self.assertEqual(self.picking_confirmed.state, "confirmed")

    def test_force_availability_nothing_to_unreserve(self):
        # Try to call the wizard from a transfer with nothing to unreserve
        wiz = self.get_force_availability_wizard(self.picking_assigned)
        self.assertIn("Nothing to unreserve", wiz.warning)
        self.assertFalse(wiz.move_to_unreserve_ids)

    def test_force_availability_different_picking_type(self):
        """Unreserve the goods from a transfer with another picking type."""
        # Create a 'confirmed' transfer with type OUT
        # NOTE: we use another product to not conflict with existing transfers
        picking_out_confirmed = self._create_picking(
            self.picking_type_out,
            lines=[
                (self.product2, self.picking_type_out.default_location_src_id, 10),
            ],
            put_stock=False,
        )
        # Create an 'assigned' transfer with type OUT2
        new_picking_type_out = self.picking_type_out.copy({"sequence_code": "OUT2"})
        picking_out2_assigned = self._create_picking(
            new_picking_type_out,
            lines=[
                (self.product2, new_picking_type_out.default_location_src_id, 10),
            ],
        )
        # Try first with the "Same operation type" option enabled (default)
        wiz = self.get_force_availability_wizard(picking_out_confirmed)
        self.assertIn("Nothing to unreserve", wiz.warning)
        self.assertFalse(wiz.move_to_unreserve_ids)
        # Now disable the option to get the moves to unreserve
        wiz.same_picking_type = False
        self.assertEqual(wiz.move_to_unreserve_ids, picking_out2_assigned.move_lines)
        wiz.validate()
        self.assertEqual(picking_out2_assigned.state, "confirmed")
        self.assertEqual(picking_out_confirmed.state, "assigned")
