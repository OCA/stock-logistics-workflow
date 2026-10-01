# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from freezegun import freeze_time

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestStockDateDone(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "is_storable": True,
            }
        )
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.group = cls.env.ref("stock_date_done.group_date_done_editable")

    def _create_receipt(self, date_done=False):
        receipt = self.env["stock.picking"].create(
            {
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "date_done": date_done,
                "move_ids": [
                    Command.create(
                        {
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.stock_location.id,
                            "product_id": self.product.id,
                            "product_uom_qty": 10.0,
                        }
                    )
                ],
            }
        )
        receipt.action_confirm()
        receipt.move_ids.quantity = 10.0
        receipt.move_ids.picked = True
        receipt.button_validate()
        return receipt

    @freeze_time("2024-09-20 10:00:00")
    def test_date_done_propagation_on_edit(self):
        receipt = self._create_receipt()
        move = receipt.move_ids
        new_date = datetime(2024, 9, 1, 8, 0, 0)
        receipt.date_done = new_date
        # date_done -> move.date -> move_line.date, all native cascade.
        self.assertEqual(move.date, new_date)
        self.assertEqual(move.move_line_ids.date, new_date)

    def test_preset_date_done_honored(self):
        preset = datetime(2024, 8, 1, 8, 0, 0)
        receipt = self._create_receipt(date_done=preset)
        # Native stamps now() at validation; our override restores the preset.
        self.assertEqual(receipt.date_done, preset)
        self.assertEqual(receipt.move_ids.date, preset)
        self.assertEqual(receipt.move_ids.move_line_ids.date, preset)

    @freeze_time("2024-09-20 10:00:00")
    def test_origin_date_done_captured_and_immutable(self):
        receipt = self._create_receipt()
        origin = receipt.origin_date_done
        self.assertEqual(origin, datetime(2024, 9, 20, 10, 0, 0))
        # Editing the effective date must not change the audit origin.
        receipt.date_done = datetime(2024, 9, 1, 8, 0, 0)
        self.assertEqual(receipt.origin_date_done, origin)

    def test_date_done_edited_flag(self):
        # Drives the visibility of Original Effective Date: only flagged once
        # the effective date actually diverges from the captured origin.
        receipt = self._create_receipt()
        self.assertFalse(receipt.date_done_edited)
        receipt.date_done = receipt.date_done - timedelta(days=1)
        receipt.invalidate_recordset(["date_done_edited"])
        self.assertTrue(receipt.date_done_edited)

    def test_permission_gating_on_done_picking(self):
        receipt = self._create_receipt()
        # Unlock so native is_date_editable is True; the group is then the only
        # remaining gate that our field adds on top.
        receipt.is_locked = False
        user = self.env["res.users"].create(
            {
                "name": "Stock User",
                "login": "stock_user_date_done",
                "group_ids": [Command.link(self.env.ref("stock.group_stock_user").id)],
            }
        )
        self.assertFalse(receipt.with_user(user).is_date_done_editable)
        user.group_ids = [Command.link(self.group.id)]
        self.assertTrue(receipt.with_user(user).is_date_done_editable)

    @freeze_time("2024-09-20 10:00:00")
    def test_scrap_preset_date_and_origin(self):
        self._create_receipt()
        scrap_date = datetime(2024, 9, 5, 8, 0, 0)
        scrap = self.env["stock.scrap"].create(
            {
                "product_id": self.product.id,
                "scrap_qty": 2.0,
                "date_done": scrap_date,
            }
        )
        scrap.do_scrap()
        # Effective date kept and propagated to the scrap move + line.
        self.assertEqual(scrap.date_done, scrap_date)
        done_move = scrap.move_ids.filtered(lambda m: m.state == "done")
        self.assertEqual(done_move.date, scrap_date)
        self.assertEqual(done_move.move_line_ids.date, scrap_date)
        # Origin captures the true processing timestamp, immutable.
        self.assertEqual(scrap.origin_date_done, datetime(2024, 9, 20, 10, 0, 0))
        scrap.date_done = datetime(2024, 8, 1, 8, 0, 0)
        self.assertEqual(scrap.origin_date_done, datetime(2024, 9, 20, 10, 0, 0))
        # Editing a done scrap's date propagates to its move.
        self.assertEqual(
            scrap.move_ids.filtered(lambda m: m.state == "done").date,
            datetime(2024, 8, 1, 8, 0, 0),
        )

    @freeze_time("2024-09-20 10:00:00")
    def test_scrap_without_preset_not_flagged_as_edited(self):
        # A normal scrap (no effective date set up front): date_done is the real
        # processing time, equals origin, and is NOT flagged as edited.
        self._create_receipt()
        scrap = self.env["stock.scrap"].create(
            {"product_id": self.product.id, "scrap_qty": 2.0}
        )
        scrap.do_scrap()
        self.assertEqual(scrap.date_done, datetime(2024, 9, 20, 10, 0, 0))
        self.assertEqual(scrap.origin_date_done, scrap.date_done)
        self.assertFalse(scrap.date_done_edited)
