# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBatchSubstate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Test substates
        draft_target_state = cls.env.ref(
            "stock_picking_batch_substate.target_state_value_batch_draft"
        )
        cls.draft_substate = cls.env["base.substate"].create(
            {
                "name": "Draft Substate 1",
                "target_state_value_id": draft_target_state.id,
                "sequence": 1,
            }
        )
        in_progress_target_state = cls.env.ref(
            "stock_picking_batch_substate.target_state_value_batch_in_progress"
        )
        cls.in_progress_substate1 = cls.env["base.substate"].create(
            {
                "name": "In Progress Substate 1",
                "target_state_value_id": in_progress_target_state.id,
                "sequence": 2,
            }
        )
        cls.in_progress_substate2 = cls.env["base.substate"].create(
            {
                "name": "In Progress Substate 2",
                "target_state_value_id": in_progress_target_state.id,
                "sequence": 3,
            }
        )
        done_target_state = cls.env.ref(
            "stock_picking_batch_substate.target_state_value_batch_done"
        )
        cls.done_substate = cls.env["base.substate"].create(
            {
                "name": "Done Substate 1",
                "target_state_value_id": done_target_state.id,
                "sequence": 4,
            }
        )
        # Test batch
        picking_type_out = cls.env["stock.picking.type"].search(
            [("code", "=", "outgoing"), ("company_id", "=", cls.env.company.id)],
            limit=1,
        )
        product = cls.env["product.product"].create({"name": "Test Product"})
        cls.picking1, cls.picking2 = cls.env["stock.picking"].create(
            [
                {
                    "picking_type_id": picking_type_out.id,
                    "move_ids": [
                        Command.create(
                            {
                                "product_id": product.id,
                                "product_uom_qty": 10,
                            }
                        )
                    ],
                },
                {
                    "picking_type_id": picking_type_out.id,
                    "move_ids": [
                        Command.create(
                            {
                                "product_id": product.id,
                                "product_uom_qty": 20,
                            }
                        )
                    ],
                },
            ]
        )
        cls.batch = cls.env["stock.picking.batch"].create(
            {
                "name": "Batch 1",
                "picking_ids": [
                    Command.link(cls.picking1.id),
                    Command.link(cls.picking2.id),
                ],
            }
        )

    def test_stock_picking_batch_substate_creation(self):
        self.assertEqual(self.batch.state, "draft")
        self.assertEqual(self.batch.substate_id, self.draft_substate)

        # Block substate not corresponding to draft state
        with self.assertRaises(ValidationError):
            self.batch.substate_id = self.in_progress_substate1

        # Test that validation of batch change substate_id
        self.batch.action_confirm()
        self.assertEqual(self.batch.state, "in_progress")
        self.assertEqual(self.batch.substate_id, self.in_progress_substate1)

        # If the state computation does not change its value,
        # it should not change the substate
        self.batch.substate_id = self.in_progress_substate2
        self.picking2.action_cancel()  # Triggers the recomputation despite no change
        self.assertEqual(self.batch.state, "in_progress")
        self.assertEqual(self.batch.substate_id, self.in_progress_substate2)

        # Test that change of state by a compute method set the correct substate
        self.batch.action_done()
        self.assertEqual(self.batch.state, "done")
        self.assertEqual(self.batch.substate_id, self.done_substate)

        # Test that substate_id is set to false if
        # there is not substate corresponding to state
        self.batch.action_cancel()
        self.assertEqual(self.batch.state, "cancel")
        self.assertFalse(self.batch.substate_id)
