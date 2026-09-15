# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPickingLinkWizard(TransactionCase):
    def setUp(self):
        super().setUp()
        # Create test product
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

        # Enable outgoing pickings in portal
        outgoing_type = self.env["stock.picking.type"].search(
            [("code", "=", "outgoing")], limit=1
        )
        outgoing_type.portal_visible = True

        # Create portal user
        portal_group = self.env.ref("base.group_portal")
        self.user = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Portal User",
                    "login": "portal_user",
                    "password": "portal",
                    "groups_id": [(6, 0, [portal_group.id])],
                }
            )
        )

        # Create sale order and related picking
        so = self.env["sale.order"].create(
            {
                "partner_id": self.user.partner_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 2,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        so.action_confirm()
        self.picking = so.picking_ids[0]

        # Create wizard with required picking_id
        self.wizard = self.env["picking.link.wizard"].create(
            {
                "picking_id": self.picking.id,
            }
        )

    def test_default_get_sets_picking_id_from_context(self):
        """Test that default_get sets picking_id from context"""
        wizard = (
            self.env["picking.link.wizard"]
            .with_context(active_id=self.picking.id, active_model="stock.picking")
            .new({})
        )

        defaults = wizard.default_get(["picking_id"])
        self.assertEqual(defaults.get("picking_id"), self.picking.id)

    def test_compute_link_generates_valid_url(self):
        """Test that _compute_link generates valid portal URL"""
        self.wizard._compute_link()
        link = self.wizard.link

        # Verify URL components
        self.assertTrue(link.startswith(self.picking.get_base_url()))
        self.assertIn(f"/my/stock_operations/{self.picking.id}", link)
        self.assertIn(f"access_token={self.picking.access_token}", link)

        # Verify token exists and has reasonable length
        self.assertTrue(len(self.picking.access_token) > 10)

        # Verify full URL format
        expected_url = (
            f"{self.picking.get_base_url()}"
            f"{self.picking.access_url}?"
            f"access_token={self.picking.access_token}"
        )
        self.assertEqual(link, expected_url)
