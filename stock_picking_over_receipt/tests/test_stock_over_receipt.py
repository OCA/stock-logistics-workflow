# Copyright 2026 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import RecordCapturer
from odoo.tools import formatLang

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestStockOverReceipt(BaseCommon):
    """Receipts above demand can be split and validated, and warn about it."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product_a, cls.product_b = cls.env["product.product"].create(
            [
                {"name": "Product A", "is_storable": True},
                {"name": "Product B", "is_storable": True},
            ]
        )
        cls.responsible = cls.env.ref("base.user_admin")

    def _make_receipt(self, received_a, received_b, creator=None, picking_type=None):
        """Receive the given quantities on a receipt of 1000 A and 1000 B.

        With `picking_type`, a transfer of that type is used instead.
        """
        picking_type = picking_type or self.warehouse.in_type_id
        location = picking_type.default_location_src_id
        location_dest = picking_type.default_location_dest_id
        picking = (
            self.env["stock.picking"]
            .with_user(creator or self.env.user)
            .create(
                {
                    "picking_type_id": picking_type.id,
                    "location_id": location.id,
                    "location_dest_id": location_dest.id,
                    "user_id": self.responsible.id,
                    "move_ids": [
                        Command.create(
                            {
                                "product_id": product.id,
                                "product_uom_qty": 1000,
                                "location_id": location.id,
                                "location_dest_id": location_dest.id,
                            }
                        )
                        for product in (self.product_a, self.product_b)
                    ],
                }
            )
            .with_env(self.env)
        )
        picking.action_confirm()
        move_a, move_b = picking.move_ids
        move_a.quantity = received_a
        move_b.quantity = received_b
        return picking

    def test_split_over_receipt(self):
        """A receipt with a line above its demand can be split.

        Scenario:
            1. Receive 1200 A (or 2000 A) and 500 B on a receipt of 1000 A
               and 1000 B.
            2. Split it.
        Expected:
            - The receipt keeps all of A and the 500 B received.
            - The new receipt holds the 500 B left.
        """
        for received_a in (1200, 2000):
            with self.subTest(received_a=received_a):
                picking = self._make_receipt(received_a, 500)
                picking.action_split_transfer()
                self.assertRecordValues(
                    picking.move_ids,
                    [
                        {
                            "product_id": self.product_a.id,
                            "product_uom_qty": 1000,
                            "quantity": received_a,
                        },
                        {
                            "product_id": self.product_b.id,
                            "product_uom_qty": 500,
                            "quantity": 500,
                        },
                    ],
                )
                self.assertRecordValues(
                    picking.backorder_ids.move_ids,
                    [{"product_id": self.product_b.id, "product_uom_qty": 500}],
                )

    def test_split_over_receipt_nothing_open(self):
        """A receipt with nothing left open cannot be split.

        Scenario:
            1. Receive 1200 A and 1000 B on a receipt of 1000 A and 1000 B.
            2. Split it.
        Expected:
            - The split is refused: all demand is done.
        """
        picking = self._make_receipt(1200, 1000)
        with self.assertRaisesRegex(UserError, "Nothing to split, all demand is done"):
            picking.action_split_transfer()

    def test_split_receipt_nothing_received(self):
        """A receipt with nothing received is still refused by core.

        Scenario:
            1. Receive nothing on a receipt of 1000 A and 1000 B.
            2. Split it.
        Expected:
            - The split is refused: nothing to split.
        """
        picking = self._make_receipt(0, 0)
        with self.assertRaisesRegex(UserError, "Nothing to split. Fill the quantities"):
            picking.action_split_transfer()

    def test_split_over_delivery(self):
        """A delivery with a line above its demand still cannot be split.

        Scenario:
            1. Deliver 1200 A and 500 B on a delivery of 1000 A and 1000 B.
            2. Split it.
        Expected:
            - The split is refused by core: quantities above demand.
        """
        picking = self._make_receipt(1200, 500, picking_type=self.warehouse.out_type_id)
        with self.assertRaisesRegex(UserError, "quantities done can't be above demand"):
            picking.action_split_transfer()

    def test_validate_over_receipt_activity(self):
        """Validating a receipt above demand warns its responsible.

        Scenario:
            1. Receive 1200 A and 1000 B on a receipt of 1000 A and 1000 B.
            2. Validate it.
        Expected:
            - The receipt is done with 1200 A.
            - A To-Do activity is scheduled on it for its responsible.
        """
        picking = self._make_receipt(1200, 1000)
        with RecordCapturer(self.env["mail.activity"]) as activities:
            picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.move_ids[0].quantity, 1200)
        self.assertRecordValues(
            activities.records,
            [
                {
                    "res_id": picking.id,
                    "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                    "user_id": self.responsible.id,
                }
            ],
        )
        # Formatted as the database's language is (e.g. 1'200.00 in Switzerland).
        received, demand = (
            formatLang(self.env, qty, dp="Product Unit") for qty in (1200, 1000)
        )
        self.assertIn(
            f"Product A: {received} / {demand} Units", activities.records.note
        )

    def test_validate_over_receipt_activity_no_responsible(self):
        """Without a responsible, the creator of the receipt is warned.

        Scenario:
            1. A user creates a receipt of 1000 A and 1000 B, with no
               responsible, and 500 A and 1000 B are received.
            2. Another user splits it, and receives 700 A on the new receipt.
            3. Validate the new receipt.
        Expected:
            - The activity is scheduled for the user who created the first
              receipt, not for the one who split it.
        """
        picking = self._make_receipt(500, 1000, creator=self.responsible)
        picking.user_id = False
        picking.action_split_transfer()
        backorder = picking.backorder_ids
        backorder.move_ids.quantity = 700
        with RecordCapturer(self.env["mail.activity"]) as activities:
            backorder.button_validate()
        self.assertNotEqual(backorder.create_uid, self.responsible)
        self.assertEqual(activities.records.user_id, self.responsible)

    def test_validate_exact_receipt_no_activity(self):
        """A receipt received as ordered schedules no activity."""
        picking = self._make_receipt(1000, 1000)
        with RecordCapturer(self.env["mail.activity"]) as activities:
            picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertFalse(activities.records)
