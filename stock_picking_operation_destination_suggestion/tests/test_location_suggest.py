# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.tests import Form

from .common import PickingDestinationSuggestCommon


class TestPickingDestinationSuggest(PickingDestinationSuggestCommon):
    def test_picking_suggest(self):
        self._create_procurement()
        self.move = self.env["stock.move"].search(
            [
                ("location_id", "=", self.stock.id),
                ("product_id", "=", self.product.id),
                ("state", "=", "assigned"),
            ]
        )
        self.assertTrue(self.move)
        self.move.move_line_ids.qty_done = 5.0
        # Put products in a particular location
        location_1 = self.env["stock.location"].search([("barcode", "=", "L#OUT.1")])
        self.move.move_line_ids.location_dest_id = location_1
        self.move._action_done()

        self.move_out = self.env["stock.move"].search(
            [("location_id", "=", self.output.id), ("product_id", "=", self.product.id)]
        )

        self.assertTrue(self.move_out)
        self.assertTrue(self.move_out.move_line_ids)

        self._create_procurement()
        self.move = self.env["stock.move"].search(
            [
                ("location_id", "=", self.stock.id),
                ("product_id", "=", self.product.id),
                ("state", "=", "assigned"),
            ]
        )
        self.assertTrue(self.move)
        self.assertEqual(
            location_1, self.move.picking_id.destination_location_suggestion_ids
        )

        # Check action
        action = self.move.picking_id.suggest_destination()
        self.assertEqual(
            "stock.picking.operation.destination.suggestion", action.get("res_model")
        )

        # Check wizard
        wizard = (
            self.env["stock.picking.operation.destination.suggestion"]
            .with_context(
                active_id=self.move.picking_id.id, active_model="stock.picking"
            )
            .create({})
        )
        self.assertEqual(self.move.picking_id, wizard.picking_id)
        self.assertEqual(location_1, wizard.destination_location_suggestion_ids)
        self.assertFalse(wizard.move_line_ids)
        self.move.move_line_ids.qty_done = 5.0
        wizard.invalidate_recordset()
        self.assertTrue(wizard.move_line_ids)
        self.assertEqual(self.move.move_line_ids, wizard.move_line_ids)

        with Form(wizard) as wizard_form:
            wizard_form.chosen_location_suggestion_id = (
                wizard.destination_location_suggestion_ids
            )

        wizard.doit()
        self.assertEqual(location_1, self.move.move_line_ids.location_dest_id)

        # Check wrong model wizard
        with self.assertRaises(ValidationError) as error:
            wizard = (
                self.env["stock.picking.operation.destination.suggestion"]
                .with_context(
                    active_id=self.move.picking_id.id, active_model="stock.picking.type"
                )
                .create({})
            )
        self.assertEqual(
            error.exception.args[0],
            "You are not launching the destination suggestion from a Stock Picking",
        )

    def test_picking_suggest_void(self):
        self._create_procurement()
        self.move = self.env["stock.move"].search(
            [
                ("location_id", "=", self.stock.id),
                ("product_id", "=", self.product.id),
                ("state", "=", "assigned"),
            ]
        )
        self.assertTrue(self.move)
        self.move.move_line_ids.qty_done = 5.0
        # Put products in a particular location
        location_1 = self.env["stock.location"].search([("barcode", "=", "L#OUT.1")])
        self.move.move_line_ids.location_dest_id = location_1
        self.move._action_done()

        # Create an other partner
        partner_2 = self.env["res.partner"].create({"name": "Test 2"})
        self.group = self.env["procurement.group"].create(
            {
                "name": "Group 2",
                "partner_id": partner_2.id,
            }
        )
        self._create_procurement(group_id=self.group)
        self.move = self.env["stock.move"].search(
            [
                ("location_id", "=", self.stock.id),
                ("product_id", "=", self.product.id),
                ("partner_id", "=", partner_2.id),
                ("state", "=", "assigned"),
            ]
        )
        self.assertTrue(self.move)
        self.assertFalse(self.move.picking_id.destination_location_suggestion_ids)
