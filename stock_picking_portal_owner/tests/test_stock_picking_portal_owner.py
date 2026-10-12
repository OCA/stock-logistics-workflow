# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo import Command
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo.tests import tagged

from odoo.addons.stock_picking_portal.tests.test_stock_picking_portal import (
    TestStockPickingPortal,
)
from odoo.addons.stock_picking_portal_owner.controllers.portal import (
    StockPickingPortalOwner,
)
from odoo.addons.website.tools import MockRequest


@tagged("post_install", "-at_install")
class TestStockPickingPortalOwner(TestStockPickingPortal):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.CustomerPortalController = StockPickingPortalOwner()
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

    def test_prepare_rendering_values_all_conditions(self):
        """Test all IF conditions in
        _prepare_stock_operations_portal_owner_rendering_values."""
        self._configure_portal_operations()

        # Setup data for filtering
        picking_draft = self._get_picking(self.owner_user.partner_id)
        picking_draft.write({"scheduled_date": "2026-10-01 10:00:00", "state": "draft"})

        picking_done = self._get_picking(self.owner_user.partner_id)
        # Fix: Write the scheduled date BEFORE changing the state to 'done'
        picking_done.write({"scheduled_date": "2026-11-01 10:00:00"})
        picking_done.write({"state": "done"})

        with MockRequest(self.stock_picking_obj.with_user(self.owner_user).env):
            values_default = self.controller._prepare_stock_operations_portal_owner_rendering_values()  # noqa: E501
            self.assertEqual(values_default.get("sortby"), "date")

            values_dates = (
                self.controller._prepare_stock_operations_portal_owner_rendering_values(
                    date_from="2026-09-01", date_to="2026-10-31"
                )
            )
            self.assertIn(picking_draft, values_dates["stock_operation_ids"])
            self.assertNotIn(picking_done, values_dates["stock_operation_ids"])

            values_state = (
                self.controller._prepare_stock_operations_portal_owner_rendering_values(
                    move_state="done"
                )
            )
            self.assertIn(picking_done, values_state["stock_operation_ids"])
            self.assertNotIn(picking_draft, values_state["stock_operation_ids"])

            values_state_all = (
                self.controller._prepare_stock_operations_portal_owner_rendering_values(
                    move_state="all"
                )
            )
            self.assertIn(picking_draft, values_state_all["stock_operation_ids"])
            self.assertIn(picking_done, values_state_all["stock_operation_ids"])

    def test_portal_owner_operation_page_reports(self):
        """Test the report_type IF condition for html, pdf, and text."""
        self._configure_portal_operations()
        picking = self._get_picking(self.owner_user.partner_id)

        with MockRequest(self.stock_picking_obj.with_user(self.owner_user).env):
            with patch.object(
                type(self.controller),
                "_show_report",
                return_value="mocked_report_content",
            ):
                res_html = self.controller.portal_owner_stock_operation_page(
                    picking.id, report_type="html"
                )
                self.assertEqual(res_html.data, b"mocked_report_content")

                res_pdf = self.controller.portal_owner_stock_operation_page(
                    picking.id, report_type="pdf"
                )
                self.assertEqual(res_pdf.data, b"mocked_report_content")

                res_text = self.controller.portal_owner_stock_operation_page(
                    picking.id, report_type="text"
                )
                self.assertEqual(res_text.data, b"mocked_report_content")

    def test_portal_owner_operation_page_access_denied_picking_type(self):
        """Test the IF condition that raises AccessDenied
        if picking_type is not visible."""
        picking = self._get_picking(self.owner_user.partner_id)

        self.config_obj.create({"portal_visible_operation_ids": []}).execute()

        with MockRequest(self.stock_picking_obj.with_user(self.owner_user).env):
            with self.assertRaises(AccessDenied):
                self.controller.portal_owner_stock_operation_page(picking.id)

    @patch(
        "odoo.addons.stock_picking_portal_owner.controllers.portal._message_post_helper"
    )
    def test_portal_owner_operation_page_view_notification(self, mock_message_post):
        """Test the IF conditions that log a view notification
        if the user is a share user and hasn't visited today."""
        self._configure_portal_operations()
        picking = self._get_picking(self.owner_user.partner_id)
        picking._portal_ensure_token()
        token = picking.access_token

        with MockRequest(self.stock_picking_obj.with_user(self.owner_user).env):
            with patch.object(request, "render", return_value="mocked_page"):
                request.session = {}

                self.controller.portal_owner_stock_operation_page(
                    picking.id, access_token=token
                )
                self.assertTrue(mock_message_post.called)

                mock_message_post.reset_mock()

                self.controller.portal_owner_stock_operation_page(
                    picking.id, access_token=token
                )
                self.assertFalse(mock_message_post.called)
