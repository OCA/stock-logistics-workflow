# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestStockNotifyPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.picking_type = cls.env["stock.picking.type"].create(
            {
                "name": "Test Operation Type",
                "sequence_code": "test",
                "code": "incoming",
            }
        )
        cls.user = new_test_user(
            cls.env, "jon", email="json.snow@westeros.test", notification_type="inbox"
        )
        cls.notification_template = cls.env[
            "stock.picking.notification.template"
        ].create(
            {
                "picking_type_id": cls.picking_type.id,
                "user_ids": [(6, 0, cls.user.ids)],
                "allow_notify_confirmed": False,
                "allow_notify_assigned": False,
            }
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
            }
        )

    def get_bus_notifications(self):
        """
        Return found bus notifications
        """
        return self.env["bus.bus"].search(
            [("channel", "=", self.user.notify_info_channel_name)]
        )

    def call_post_commit_hooks(self):
        """
        manually calls postcommit hooks defined with the decorator @after_commit
        """
        funcs = self.env.cr.postcommit._funcs.copy()
        while funcs:
            func = funcs.popleft()
            func()

    def test_picking_send_notification(self):
        """
        Send notification picking with default message
        """
        self.notification_template.write(
            {
                "allow_notify_draft": True,
                "allow_notify_assigned": True,
            }
        )
        existing = self.get_bus_notifications()

        picking = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.stock_location.id,
                "picking_type_id": self.picking_type.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": "test",
                "location_id": self.stock_location.id,
                "location_dest_id": self.stock_location.id,
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "picking_id": picking.id,
                "picking_type_id": self.picking_type.id,
            }
        )
        picking.action_confirm()
        # flush and clear everything for the new "transaction"
        self.env.invalidate_all()

        try:
            # enter to test mode because postcommit create new cr
            self.env.registry.enter_test_mode(self.cr)
            self.call_post_commit_hooks()
        finally:
            self.env.registry.leave_test_mode()

        news = self.get_bus_notifications() - existing
        self.assertEqual(1, len(news))
        payload = json.loads(news.message)["payload"][0]
        self.assertEqual(payload["title"], picking.name)
        self.assertEqual(payload["action"]["res_id"], picking.id)

    def test_picking_custom_messge_send_notification(self):
        """
        Send notification picking with custom message
        """
        new_template = self.notification_template.copy()
        self.notification_template.write(
            {
                "allow_notify_draft": True,
            }
        )
        # prepare another rule to send custom message
        new_template.write(
            {
                "allow_notify_assigned": True,
                "message": "test",
            }
        )
        existing = self.get_bus_notifications()

        picking = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.stock_location.id,
                "picking_type_id": self.picking_type.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": "test",
                "location_id": self.stock_location.id,
                "location_dest_id": self.stock_location.id,
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "picking_id": picking.id,
                "picking_type_id": self.picking_type.id,
            }
        )
        picking.action_confirm()
        # flush and clear everything for the new "transaction"
        self.env.invalidate_all()

        try:
            # enter to test mode because postcommit create new cr
            self.env.registry.enter_test_mode(self.cr)
            self.call_post_commit_hooks()
        finally:
            self.env.registry.leave_test_mode()

        news = self.get_bus_notifications() - existing

        # only one notification was sent
        self.assertEqual(1, len(news))
        payload = json.loads(news.message)["payload"][0]
        self.assertEqual(payload["title"], picking.name)
        self.assertEqual(payload["message"], "test")

    def test_send_picking_notification_regex(self):
        """
        Send notification by regex
        """
        new_template = self.notification_template.copy()

        # set priority and incorrect regex
        self.notification_template.write(
            {
                "allow_notify_draft": True,
                "sequence": 1,
                "source_document_regex": "test",
                "message": "rule_1",
            }
        )

        # set low priority
        new_template.write(
            {
                "allow_notify_draft": True,
                "sequence": 20,
                "message": "rule_2",
            }
        )

        existing = self.get_bus_notifications()

        self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.stock_location.id,
                "picking_type_id": self.picking_type.id,
                "origin": "origin",
            }
        )

        # flush and clear everything for the new "transaction"
        self.env.invalidate_all()

        try:
            # enter to test mode because postcommit create new cr
            self.env.registry.enter_test_mode(self.cr)
            self.call_post_commit_hooks()
        finally:
            self.env.registry.leave_test_mode()

        news = self.get_bus_notifications() - existing

        self.assertEqual(1, len(news))
        payload = json.loads(news.message)["payload"][0]
        # only second rule was applied
        self.assertEqual(payload["message"], "rule_2")
