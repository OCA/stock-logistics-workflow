# Copyright 2026  Akretion (https://www.akretion.com).
# @author Sébastien Alix <sebastien.alix@akretion.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import Command
from odoo.exceptions import AccessError

from odoo.addons.base.tests.common import BaseCommon


class TestStockReadonly(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_user = cls.env.ref("base.group_user")
        cls.group_readonly = cls.env.ref("stock_readonly.group_stock_readonly")

        cls.product = cls.env["product.product"].create(
            {"name": "Readonly Product", "is_storable": True}
        )
        cls.move = cls.env["stock.move"].create(
            {
                "product_id": cls.product.id,
                "product_uom_qty": 1.0,
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": cls.env.ref("stock.stock_location_stock").id,
            }
        )
        cls.move._assign_picking()
        cls.picking = cls.move.picking_id
        cls.lot = cls.env["stock.lot"].create(
            {"name": "LOT-RO-1", "product_id": cls.product.id}
        )
        cls.scrap = cls.env["stock.scrap"].create(
            {"product_id": cls.product.id, "scrap_qty": 1.0}
        )
        cls.scrap_reason_tag = cls.env["stock.scrap.reason.tag"].create(
            {"name": "Broken"}
        )
        cls.orderpoint = cls.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "product_min_qty": 0.0,
                "product_max_qty": 5.0,
            }
        )
        cls.package_type = cls.env["stock.package.type"].create({"name": "Box"})

        cls.user_employee = cls.env["res.users"].create(
            {
                "name": "Plain Employee",
                "login": "user_employee",
                "group_ids": [Command.link(cls.group_user.id)],
            }
        )
        cls.user_readonly = cls.env["res.users"].create(
            {
                "name": "Stock Readonly",
                "login": "stock_readonly_user",
                "group_ids": [
                    Command.link(cls.group_user.id),
                    Command.link(cls.group_readonly.id),
                ],
            }
        )

    def _visible_menus(self, user):
        return self.env["ir.ui.menu"].with_user(user).search([])._filter_visible_menus()

    def test_stock_picking_readonly(self):
        picking = self.picking.with_user(self.user_readonly)
        self.assertTrue(picking.read(["name"]))
        with self.assertRaises(AccessError):
            picking.write({"name": "Touched"})
        with self.assertRaises(AccessError):
            self.env["stock.picking"].with_user(self.user_readonly).create(
                {
                    "picking_type_id": self.env.ref("stock.picking_type_in").id,
                    "location_id": self.env.ref("stock.stock_location_suppliers").id,
                    "location_dest_id": self.env.ref("stock.stock_location_stock").id,
                }
            )

    def test_stock_move_readonly(self):
        move = self.move.with_user(self.user_readonly)
        self.assertTrue(move.read(["product_uom_qty"]))
        with self.assertRaises(AccessError):
            move.write({"product_uom_qty": 2.0})
        with self.assertRaises(AccessError):
            self.env["stock.move"].with_user(self.user_readonly).create(
                {
                    "product_id": self.product.id,
                    "product_uom_qty": 1.0,
                    "location_id": self.env.ref("stock.stock_location_suppliers").id,
                    "location_dest_id": self.env.ref("stock.stock_location_stock").id,
                }
            )

    def test_stock_lot_readonly(self):
        lot = self.lot.with_user(self.user_readonly)
        self.assertTrue(lot.read(["name"]))
        with self.assertRaises(AccessError):
            lot.write({"name": "Touched"})
        with self.assertRaises(AccessError):
            self.env["stock.lot"].with_user(self.user_readonly).create(
                {"name": "Sneaky Lot", "product_id": self.product.id}
            )

    def test_stock_scrap_readonly(self):
        scrap = self.scrap.with_user(self.user_readonly)
        self.assertTrue(scrap.read(["scrap_qty"]))
        with self.assertRaises(AccessError):
            scrap.write({"scrap_qty": 2.0})
        with self.assertRaises(AccessError):
            self.env["stock.scrap"].with_user(self.user_readonly).create(
                {"product_id": self.product.id, "scrap_qty": 1.0}
            )

    def test_stock_scrap_reason_tag_readonly(self):
        tag = self.scrap_reason_tag.with_user(self.user_readonly)
        self.assertTrue(tag.read(["name"]))
        with self.assertRaises(AccessError):
            tag.write({"name": "Touched"})
        with self.assertRaises(AccessError):
            self.env["stock.scrap.reason.tag"].with_user(self.user_readonly).create(
                {"name": "Sneaky Tag"}
            )

    def test_stock_warehouse_orderpoint_readonly(self):
        orderpoint = self.orderpoint.with_user(self.user_readonly)
        self.assertTrue(orderpoint.read(["product_min_qty"]))
        with self.assertRaises(AccessError):
            orderpoint.write({"product_min_qty": 1.0})
        with self.assertRaises(AccessError):
            self.env["stock.warehouse.orderpoint"].with_user(self.user_readonly).create(
                {
                    "product_id": self.product.id,
                    "location_id": self.env.ref("stock.stock_location_stock").id,
                    "product_min_qty": 0.0,
                    "product_max_qty": 5.0,
                }
            )

    def test_stock_package_type_readonly(self):
        package_type = self.package_type.with_user(self.user_readonly)
        self.assertTrue(package_type.read(["name"]))
        with self.assertRaises(AccessError):
            package_type.write({"name": "Touched"})
        with self.assertRaises(AccessError):
            self.env["stock.package.type"].with_user(self.user_readonly).create(
                {"name": "Sneaky Box"}
            )

    def test_stock_package_history_readonly(self):
        history = self.env["stock.package.history"].with_user(self.user_readonly)
        history.check_access("read")
        with self.assertRaises(AccessError):
            history.check_access("write")
        with self.assertRaises(AccessError):
            history.check_access("create")

    def test_stock_traceability_report_readonly(self):
        report = self.env["stock.traceability.report"].with_user(self.user_readonly)
        report.check_access("read")
        lines = report.get_main_lines()
        self.assertIsInstance(lines, list)

    def test_employee_without_group_cannot_read_picking(self):
        with self.assertRaises(AccessError):
            self.picking.with_user(self.user_employee).read(["name"])

    def test_menus_visible_for_readonly_user(self):
        visible = self._visible_menus(self.user_readonly)
        for xmlid in (
            "stock.menu_stock_root",
            "stock.menu_stock_warehouse_mgmt",
            "stock.menu_stock_transfers",
            "stock.in_picking",
            "stock.out_picking",
        ):
            self.assertIn(self.env.ref(xmlid), visible)
        self.assertNotIn(self.env.ref("stock.menu_stock_config_settings"), visible)
        # The "Internal" transfers menu is gated by the multi-locations
        # feature group, which still applies to read-only users.
        self.assertNotIn(self.env.ref("stock.int_picking"), visible)

    def test_root_menu_not_visible_for_plain_employee(self):
        visible = self._visible_menus(self.user_employee)
        self.assertNotIn(self.env.ref("stock.menu_stock_root"), visible)

    def test_menu_actions_execution(self):
        for xmlid in (
            "stock.in_picking",
            "stock.out_picking",
            "stock.menu_action_inventory_tree",
        ):
            action = self.env.ref(xmlid).action
            with self.assertRaises(AccessError):
                action.with_user(self.user_employee).run()
            action_res = action.with_user(self.user_readonly).run()
            self.assertTrue(action_res)
