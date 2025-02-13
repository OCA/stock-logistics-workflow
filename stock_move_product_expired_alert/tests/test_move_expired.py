# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo.addons.base.tests.common import BaseCommon


class TestStockMove(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "tracking": "lot",
                "use_expiration_date": True,
            }
        )
        cls.suppliers = cls.env.ref("stock.stock_location_suppliers")
        cls.stock = cls.env.ref("stock.stock_location_stock")

        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_in.check_expired_product_alert = "alert_date"

        cls.team = cls.env["mail.activity.team"].create(
            {
                "name": "Test Team",
            }
        )

        cls.user = cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
            }
        )
        cls.member_ids = cls.env.user
        cls.env.company.check_expired_product_alert_team_id = cls.team
        cls.lot = cls._create_lot()

    @classmethod
    def _create_lot(cls):
        return cls.env["stock.lot"].create(
            {
                "name": "Test",
                "product_id": cls.product.id,
                "expiration_date": "2025-01-30",
                "removal_date": "2025-01-20",
                "alert_date": "2025-01-15",
            }
        )

    @classmethod
    def _create_move(cls):
        return cls.env["stock.move"].create(
            {
                "name": "Product Test",
                "picking_type_id": cls.picking_type_in.id,
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.suppliers.id,
                "location_dest_id": cls.stock.id,
                "product_uom_qty": 10.0,
            }
        )

    @freeze_time("2025-01-31")
    def test_move_expired(self):
        # Check if
        move = self._create_move()
        move._action_confirm()
        move._assign_picking()
        move.move_line_ids.lot_id = self.lot
        move.quantity_done = move.product_uom_qty
        activities_before = move.picking_id.activity_ids
        move._action_done()
        activities_after = move.picking_id.activity_ids - activities_before
        self.assertEqual(1, len(activities_after))
        self.assertEqual(self.team, activities_after.team_id)

    @freeze_time("2025-01-10")
    def test_move_not_expired(self):
        move = self._create_move()
        move._action_confirm()
        move._assign_picking()
        move.move_line_ids.lot_id = self.lot
        move.quantity_done = move.product_uom_qty
        activities_before = move.picking_id.activity_ids
        move._action_done()
        activities_after = move.picking_id.activity_ids - activities_before
        self.assertEqual(0, len(activities_after))
