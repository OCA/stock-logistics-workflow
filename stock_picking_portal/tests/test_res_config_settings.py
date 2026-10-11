# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPortalConfigSettings(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PickingType = cls.env["stock.picking.type"]
        cls.type_outgoing = cls.PickingType.search([("code", "=", "outgoing")], limit=1)
        cls.type_incoming = cls.PickingType.search([("code", "=", "incoming")], limit=1)
        cls.type_outgoing.write({"portal_visible": False})
        cls.type_incoming.write({"portal_visible": False})
        cls.Settings = cls.env["res.config.settings"]

    def test_set_values_updates_portal_flags(self):
        """Test that set_values() correctly updates portal_visible flags."""
        # Initial state check
        self.assertFalse(self.type_outgoing.portal_visible)
        self.assertFalse(self.type_incoming.portal_visible)

        # Test setting outgoing visible
        settings = self.Settings.create(
            {"portal_visible_operation_ids": [(6, 0, [self.type_outgoing.id])]}
        )
        settings.set_values()

        self.assertTrue(
            self.type_outgoing.portal_visible,
            "Outgoing type should be visible after set_values()",
        )
        self.assertFalse(
            self.type_incoming.portal_visible, "Incoming type should remain invisible"
        )

        # Test switching to incoming
        settings.write(
            {"portal_visible_operation_ids": [(6, 0, [self.type_incoming.id])]}
        )
        settings.set_values()

        self.assertFalse(
            self.type_outgoing.portal_visible,
            "Outgoing type should be invisible after update",
        )
        self.assertTrue(
            self.type_incoming.portal_visible, "Incoming type should become visible"
        )

    def test_get_values_reflects_portal_flags(self):
        """Test that get_values() returns correct visible operation IDs."""
        # Set both visible
        self.type_outgoing.portal_visible = True
        self.type_incoming.portal_visible = True

        values = self.Settings.get_values()
        visible_ids = values.get("portal_visible_operation_ids", [])

        self.assertEqual(
            set(visible_ids),
            {self.type_outgoing.id, self.type_incoming.id},
            "Should return IDs of both visible types",
        )

        # Set incoming invisible
        self.type_incoming.portal_visible = False
        values = self.Settings.get_values()
        visible_ids = values.get("portal_visible_operation_ids", [])

        self.assertIn(
            self.type_outgoing.id,
            visible_ids,
            "Outgoing ID should still be in visible list",
        )
        self.assertNotIn(
            self.type_incoming.id,
            visible_ids,
            "Incoming ID should be excluded after making it invisible",
        )
