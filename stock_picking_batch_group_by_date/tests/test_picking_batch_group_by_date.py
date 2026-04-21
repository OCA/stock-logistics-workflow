# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from freezegun import freeze_time

from odoo import Command
from odoo.tests import TransactionCase


class TestPickingBatchPartnerEnable(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "is_storable": True,
            }
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        # Ensure there are enough products in stock
        cls.env["stock.quant"]._update_available_quantity(
            cls.product,
            cls.warehouse.lot_stock_id,
            1000,
        )
        # Enable auto_batch on picking type
        cls.picking_type = cls.warehouse.out_type_id
        cls.picking_type.write(
            {
                "auto_batch": True,
                "batch_group_by_date": True,
            }
        )

    @classmethod
    def _create_picking(cls, confirm=True, assign=True):
        """Helper to create a picking with moves"""
        picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.picking_type.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 10,
                            "product_uom": cls.product.uom_id.id,
                        }
                    )
                ],
            }
        )
        if confirm:  # pragma: no cover
            picking.action_confirm()
        if assign:  # pragma: no cover
            picking.action_assign()
        return picking

    def test_batch_group_by_date(self):
        with freeze_time("2026-01-01 12:00:00"):
            picking1 = self._create_picking()
        with freeze_time("2026-01-01 16:00:00"):
            picking2 = self._create_picking()
        self.assertEqual(picking1.batch_id, picking2.batch_id)
        self.assertEqual(
            picking1.batch_id.scheduled_date, datetime(2026, 1, 1, 12, 0, 0)
        )
        self.assertIn("01/01/2026", picking1.batch_id.description)

    def test_batch_group_by_date_with_different_dates(self):
        with freeze_time("2026-01-01 12:00:00"):
            picking1 = self._create_picking()
        with freeze_time("2026-01-02 12:00:00"):
            picking2 = self._create_picking()
        self.assertNotEqual(picking1.batch_id, picking2.batch_id)
        self.assertIn("01/01/2026", picking1.batch_id.description)
        self.assertIn("01/02/2026", picking2.batch_id.description)
        # Add additional pickings on the same dates
        with freeze_time("2026-01-01 18:00:00"):
            picking3 = self._create_picking()
        with freeze_time("2026-01-02 18:00:00"):
            picking4 = self._create_picking()
        self.assertEqual(picking1.batch_id, picking3.batch_id)
        self.assertEqual(picking2.batch_id, picking4.batch_id)

    def test_batch_group_by_date_with_different_timezone(self):
        self.warehouse.partner_id.tz = "Europe/Brussels"
        with freeze_time("2026-01-01 23:00:00"):
            picking1 = self._create_picking()
        with freeze_time("2026-01-02 01:00:00"):
            picking2 = self._create_picking()
        self.assertEqual(picking1.batch_id, picking2.batch_id)
        self.assertIn("01/02/2026", picking1.batch_id.description)
        self.assertIn("01/02/2026", picking2.batch_id.description)
