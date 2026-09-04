# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.stock_picking_portal.tests.test_stock_picking_portal import (
    TestStockPickingPortal,
)
from odoo.addons.stock_picking_portal_owner.controllers.portal import CustomerPortal
from odoo.addons.website.tools import MockRequest


@tagged("post_install", "-at_install")
class TestStockPickingPortalOwner(TestStockPickingPortal):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.CustomerPortalController = CustomerPortal()
        cls.controller = cls.CustomerPortalController
        cls.picking_type = cls.operation_types.filtered(
            lambda picking_type: picking_type.code == "outgoing"
        )[:1]
        portal_group = cls.env.ref("base.group_portal")
        cls.owner_user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Consignment Owner",
                    "login": "consignment_owner",
                    "password": "consignment_owner",
                    "groups_id": [Command.set([portal_group.id])],
                }
            )
        )
        cls.other_owner = cls.env["res.partner"].create({"name": "Other Owner"})
        cls.customer = cls.env["res.partner"].create({"name": "Picking Customer"})

    def _get_picking(self, owner=None):
        pickings = super()._get_picking()
        owner = owner or self.portal_user_1.partner_id
        pickings.write({"owner_id": owner.id, "partner_id": owner.id})
        return pickings

    def _configure_portal_operations(self):
        self.config_obj.create(
            {"portal_visible_operation_ids": self.operation_types.ids}
        ).execute()

    def test_owner_domain_only_contains_authenticated_owner_pickings(self):
        self._configure_portal_operations()
        self.owner_picking = self._get_picking(self.owner_user.partner_id)
        self.other_picking = self._get_picking(self.other_owner)
        with MockRequest(self.stock_picking_obj.with_user(self.owner_user).env):
            domain = self.controller._get_prepared_owner_operation_domain(
                self.owner_user.partner_id
            )
            pickings = self.stock_picking_obj.search(domain)

        self.assertIn(self.owner_picking, pickings)
        self.assertNotIn(self.other_picking, pickings)

    def test_owner_portal_routes_only_expose_owner_pickings(self):
        self._configure_portal_operations()
        self.owner_picking = self._get_picking(self.owner_user.partner_id)
        self.other_picking = self._get_picking(self.other_owner)
        self.authenticate(self.owner_user.login, "consignment_owner")

        response = self.url_open("/my/stock_operations/owner")
        self.assertEqual(response.status_code, 200)

        response = self.url_open(
            f"/my/stock_operations/owner/{self.owner_picking.id}",
            allow_redirects=False,
        )
        self.assertEqual(response.status_code, 200)

        response = self.url_open(
            f"/my/stock_operations/owner/{self.other_picking.id}",
            allow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)

    def test_owner_portal_independent_from_customer_portal(self):
        """A picking with partner_id != owner_id must remain visible to the
        owner through My Consigned Pickings, independently of the customer."""
        self._configure_portal_operations()
        picking = self._get_picking()
        picking.write(
            {
                "partner_id": self.customer.id,
                "owner_id": self.owner_user.partner_id.id,
            }
        )
        self.authenticate(self.owner_user.login, "consignment_owner")

        response = self.url_open("/my/stock_operations/owner")
        self.assertEqual(response.status_code, 200)

        response = self.url_open(
            f"/my/stock_operations/owner/{picking.id}",
            allow_redirects=False,
        )
        self.assertEqual(response.status_code, 200)

    def test_standard_my_pickings_flow_not_restricted(self):
        """A picking linked to the portal user via partner_id, but whose
        owner_id belongs to someone else, must remain reachable through the
        standard My Pickings flow once stock_picking_portal_owner is
        installed."""
        self._configure_portal_operations()
        picking = self._get_picking()
        picking.write({"owner_id": self.other_owner.id})
        login = self.portal_user_1.login
        self.authenticate(login, login)

        response = self.url_open("/my/stock_operations")
        self.assertEqual(response.status_code, 200)

        response = self.url_open(
            f"/my/stock_operations/{picking.id}",
            allow_redirects=False,
        )
        self.assertEqual(response.status_code, 200)

    def test_owner_portal_detail_denies_url_tampering(self):
        """Manually changing the operation id in the URL must not grant
        access to a picking owned by another owner."""
        self._configure_portal_operations()
        self.owner_picking = self._get_picking(self.owner_user.partner_id)
        self.other_picking = self._get_picking(self.other_owner)
        self.authenticate(self.owner_user.login, "consignment_owner")

        response = self.url_open(
            f"/my/stock_operations/owner/{self.other_picking.id}",
            allow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        self.assertIn("/my", response.headers.get("Location", ""))
