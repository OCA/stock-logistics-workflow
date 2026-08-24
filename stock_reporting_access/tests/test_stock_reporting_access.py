# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStockReportingAccess(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_stock_user = cls.env.ref("stock.group_stock_user")
        cls.group_stock_manager = cls.env.ref("stock.group_stock_manager")
        cls.group_reporting = cls.env.ref(
            "stock_reporting_access.group_stock_reporting_user"
        )
        cls.reporting_menu = cls.env.ref("stock.menu_warehouse_report")
        cls.user_reporting = cls.env["res.users"].create(
            {
                "name": "Test Reporting User",
                "login": "test_reporting_user",
                "groups_id": [Command.set([cls.group_reporting.id])],
            }
        )
        cls.user_stock_only = cls.env["res.users"].create(
            {
                "name": "Test Stock User",
                "login": "test_stock_user",
                "groups_id": [Command.set([cls.group_stock_user.id])],
            }
        )

    def test_reporting_menu_groups(self):
        menu_groups = self.reporting_menu.groups_id
        self.assertIn(self.group_reporting, menu_groups)
        self.assertIn(self.group_stock_manager, menu_groups)

    def test_user_reporting_can_access_menu(self):
        visible = (
            self.env["ir.ui.menu"].with_user(self.user_reporting)._visible_menu_ids()
        )
        self.assertIn(
            self.reporting_menu.id,
            visible,
            "User with reporting group should access reporting menu",
        )

    def test_user_stock_only_cannot_access_menu(self):
        visible = (
            self.env["ir.ui.menu"].with_user(self.user_stock_only)._visible_menu_ids()
        )
        self.assertNotIn(
            self.reporting_menu.id,
            visible,
            "User with only stock user group should not access menu",
        )
