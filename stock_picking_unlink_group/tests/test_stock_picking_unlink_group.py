# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase

from odoo.addons.mail.tests.common import mail_new_test_user


class TestStockPickingUnlinkGroup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.unlink_picking_group = cls.env.ref(
            "stock_picking_unlink_group.group_stock_picking_unlink"
        )
        cls.picking_type_internal = cls.env.ref("stock.picking_type_internal")
        cls.stock_user = mail_new_test_user(
            cls.env,
            name="Viktor Draven",
            login="viktor",
            email="v.d@example.com",
            notification_type="inbox",
            groups="stock.group_stock_user",
        )
        cls.stock_manager = mail_new_test_user(
            cls.env,
            name="Elena Blackthorn",
            login="elena",
            email="e.b@example.com",
            notification_type="inbox",
            groups="stock.group_stock_manager",
        )
        cls.picking = cls.env["stock.picking"].create(
            {"picking_type_id": cls.picking_type_internal.id}
        )

    def test_unlink_picking_user_not_allowed(self):
        with self.assertRaises(AccessError):
            self.picking.with_user(self.stock_user).unlink()

    def test_unlink_picking_manager_not_allowed(self):
        with self.assertRaises(AccessError):
            self.picking.with_user(self.stock_manager).unlink()

    def test_unlink_picking_user_allowed(self):
        self.stock_user.groups_id += self.unlink_picking_group
        self.picking.with_user(self.stock_user).unlink()
        self.assertFalse(self.picking.exists())

    def test_unlink_picking_manager_allowed(self):
        self.stock_manager.groups_id += self.unlink_picking_group
        self.picking.with_user(self.stock_manager).unlink()
        self.assertFalse(self.picking.exists())
