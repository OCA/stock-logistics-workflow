# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from unittest.mock import patch

from dateutil.relativedelta import relativedelta

from odoo import Command
from odoo.http import Request
from odoo.tests import HttpCase, tagged

from odoo.addons.portal.controllers import portal
from odoo.addons.stock_picking_portal.controllers.portal import CustomerPortal
from odoo.addons.website.tools import MockRequest


@tagged("post_install", "-at_install")
class TestStockPickingPortal(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.config_obj = cls.env["res.config.settings"]
        cls.stock_picking_obj = cls.env["stock.picking"]
        cls.picking_link_wizard = cls.env["picking.link.wizard"]

        company_id = cls.env.ref("base.main_company").id
        cls.CustomerPortalController = CustomerPortal()
        cls.operation_types = cls.env["stock.picking.type"].search(
            [
                ("code", "in", ["incoming", "outgoing"]),
                ("warehouse_id.company_id", "=", company_id),
            ]
        )
        portal_group = cls.env.ref("base.group_portal")
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "product_a",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "lst_price": 1000.0,
                "standard_price": 800.0,
            }
        )
        user = datetime.now().strftime("portal%Y%m%d%H%M%S")
        cls.portal_user_1 = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "login": user,
                    "email": user,
                    "name": user,
                    "password": user,
                    "groups_id": [Command.set([portal_group.id])],
                }
            )
        )

    def _get_picking(self):
        SaleOrder = self.env["sale.order"]
        so = SaleOrder.create(
            {
                "partner_id": self.portal_user_1.partner_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_a.id,
                            "product_uom_qty": 1,
                            "price_unit": self.product_a.lst_price,
                        },
                    )
                ],
            }
        )
        so.action_confirm()
        return so.picking_ids

    def test_get_report_base_filename(self):
        """Check that the report base filename is correct"""
        picking = self._get_picking()
        filename = picking._get_report_base_filename()
        self.assertEqual(
            filename,
            f"{picking.picking_type_id.name} {picking.name}",
            msg="The filename is not correct",
        )

    def test_picking_access_url(self):
        """Ensure that the access token is created and the access url is correct"""
        picking = self._get_picking()
        picking._portal_ensure_token()
        picking._compute_access_url()
        self.assertTrue(picking.access_token, msg="The access token is not created")
        self.assertEqual(
            picking.access_url,
            f"/my/stock_operations/{picking.id}",
            msg="The access url is not correct",
        )

    def test_SO_portal_access_1(self):
        """Ensure that it is possible to open Stock Operations, either using the access token
        or being connected as portal user"""

        picking = self._get_picking()
        login = None
        picking_url = "/my/stock_operations/%s" % picking.id
        self.authenticate(login, login)
        response = self.url_open(
            url=picking_url,
            allow_redirects=False,
        )
        self.assertEqual(
            response.status_code,
            303,
            "The access to the Stock Operations should be forbidden for portal users",
        )
        picking._portal_ensure_token()
        picking_token = picking.access_token
        picking_url = "%s?access_token=%s" % (picking_url, picking_token)

        response = self.url_open(
            url=picking_url,
            allow_redirects=False,
        )
        self.assertEqual(
            response.status_code,
            403,
            "The access to the Stock Operations should be forbidden for portal users",
        )

        config = self.config_obj.create(
            {
                "portal_visible_operation_ids": self.operation_types.ids,
            }
        )
        config.execute()

        response = self.url_open(
            url=picking_url,
            allow_redirects=False,
        )
        self.assertEqual(
            response.status_code,
            200,
            "The access to the Stock Operations should be allowed for portal users",
        )

    def test_SO_portal_access_2(self):
        """Check that it is possible to open Stock Operations, either using the access token
        or being connected as portal user"""

        picking = self._get_picking()
        login = self.portal_user_1.login
        picking_url = "/my/stock_operations/%s" % picking.id
        self.authenticate(login, login)

        response = self.url_open(
            url=picking_url,
            allow_redirects=False,
        )
        self.assertEqual(
            response.status_code,
            403,
            "The access to the Stock Operations should be forbidden for portal users",
        )

        config = self.config_obj.create(
            {
                "portal_visible_operation_ids": self.operation_types.ids,
            }
        )
        config.execute()

        response = self.url_open(
            url="/my/home",
            data={"csrf_token": Request.csrf_token(self)},
        )
        self.assertEqual(
            response.status_code,
            200,
            msg="Portal users should be able to access the portal",
        )
        counters = {"stock_operations_count": 0}
        data = {}
        expected_data = {
            "stock_operations_count": 1,
        }
        with MockRequest(self.stock_picking_obj.with_user(self.portal_user_1).env):
            data = self.CustomerPortalController._prepare_home_portal_values(counters)
        self.assertEqual(
            data,
            expected_data,
            msg="The counter should be correct",
        )

        response = self.url_open(
            url=picking_url,
            allow_redirects=False,
        )
        self.assertEqual(
            response.status_code,
            200,
            "The access to the Stock Operations should be allowed for portal users",
        )

        response = self.url_open(
            url="/my/stock_operations",
            allow_redirects=False,
        )
        self.assertEqual(
            response.status_code,
            200,
            "The access to the Stock Operations should be allowed for portal users",
        )
        date_begin = datetime.now() + relativedelta(days=-1)
        date_end = datetime.now() + relativedelta(days=1)
        response = self.url_open(
            url="/my/stock_operations?date_begin=%s&date_end=%s"
            % (date_begin.strftime("%Y-%m-%d"), date_end.strftime("%Y-%m-%d")),
            allow_redirects=True,
        )
        self.assertEqual(
            response.status_code,
            200,
            "The access to the Stock Operations should be allowed for portal users",
        )

        response = self.url_open(
            url=f"{picking_url}?report_type=pdf",
            allow_redirects=True,
        )
        self.assertEqual(
            response.status_code,
            200,
            "The access to the Stock Operations should be allowed for portal users",
        )

    def test_get_available_operations(self):
        """Check that the portal_visible_operation_ids are correctly set"""

        self.assertFalse(
            self.stock_picking_obj._get_available_operations(),
            msg="No operations should be available",
        )

        config = self.config_obj.create(
            {
                "portal_visible_operation_ids": self.operation_types.ids,
            }
        )
        config.execute()
        portal_visible_operation_ids = (
            self.stock_picking_obj._get_available_operations()
        )
        self.assertEqual(
            portal_visible_operation_ids,
            self.operation_types.ids,
            msg="The operations should be available",
        )

    def test_accept_picking_authenticated(self):
        """Check that the portal user can accept a picking"""
        picking = self._get_picking()
        picking._portal_ensure_token()
        access_token = picking.access_token
        redirect_url = "/my/stock_operations/%s?access_token=%s&message=sign_ok" % (
            picking.id,
            access_token,
        )
        base_url = picking.get_base_url()
        url = "/my/stock_operations/%s/accept?access_token=%s" % (
            picking.id,
            access_token,
        )
        data = {
            "params": {
                "name": self.portal_user_1.name,
            }
        }
        res = self.opener.post(base_url + url, json=data)
        result = res.json()
        self.assertEqual(
            result["result"]["error"],
            "Signature is missing.",
            msg="Should be a signature error",
        )
        e_url = "/my/stock_operations/%s/accept?" % picking.id
        res = self.opener.post(base_url + e_url, json={})
        result = res.json()
        self.assertEqual(
            result["result"]["error"],
            "Invalid Stock Operation.",
            msg="Should be a signature error",
        )

        data = {
            "params": {
                "signature": "R0lGODlhAQABAAD/ACwAAAAAAQABAAACAA==",
                "name": self.portal_user_1.name,
            }
        }
        res = self.opener.post(base_url + url, json=data)
        result = res.json()
        self.assertEqual(
            result["result"]["redirect_url"],
            redirect_url,
            msg="Should be a redirect",
        )

        data = {
            "params": {
                "signature": "R0lGODlhAQABAAD/ACwA",
                "name": self.portal_user_1.name,
            }
        }
        res = self.opener.post(base_url + url, json=data)
        result = res.json()
        self.assertEqual(
            result["result"]["error"],
            "Invalid signature data.",
            msg="Should be a signature error",
        )

    def test_generate_signature_link(self):
        """Check that the signature link is correctly generated"""
        picking = self._get_picking()
        config = self.config_obj.create(
            {
                "portal_visible_operation_ids": self.operation_types.ids,
            }
        )
        config.execute()
        picking_link = self.picking_link_wizard.create({"picking_id": picking.id})
        picking_link._compute_link()
        self.assertEqual(
            picking_link.link,
            "%s/my/stock_operations/%s?access_token=%s"
            % (picking.get_base_url(), picking.id, picking.access_token),
            msg="The signature link should be correctly generated",
        )

    def test_prepare_home_portal_values(self):
        """Comprehensive test for _prepare_home_portal_values method"""
        self.stock_picking_obj.search(
            [("partner_id", "=", self.portal_user_1.partner_id.id)]
        ).unlink()

        counters = {"stock_operations_count": 0}
        with MockRequest(self.stock_picking_obj.with_user(self.portal_user_1).env):
            data = self.CustomerPortalController._prepare_home_portal_values(counters)

        self.assertEqual(
            data.get("stock_operations_count"),
            "0",
            "Should return '0' when no operations exist",
        )

        self._get_picking()
        with MockRequest(self.stock_picking_obj.with_user(self.portal_user_1).env):
            data = self.CustomerPortalController._prepare_home_portal_values(counters)

        self.assertEqual(
            data.get("stock_operations_count"),
            "0",
            "Should return '0' when operations exist but not configured",
        )

        self.config_obj.create(
            {
                "portal_visible_operation_ids": self.operation_types.ids,
            }
        ).execute()

        with MockRequest(self.stock_picking_obj.with_user(self.portal_user_1).env):
            data = self.CustomerPortalController._prepare_home_portal_values(counters)

        self.assertIsInstance(
            data.get("stock_operations_count"),
            int,
            "Should return integer count when configured",
        )
        self.assertGreater(
            data.get("stock_operations_count"), 0, "Count should be greater than 0"
        )

    def test_prepare_home_portal_values_counter_not_included(self):
        """Test when stock_operations_count is not in counters"""
        self.config_obj.create(
            {
                "portal_visible_operation_ids": self.operation_types.ids,
            }
        ).execute()
        self._get_picking()

        counters = {"other_counter": 0}

        with MockRequest(self.stock_picking_obj.with_user(self.portal_user_1).env):
            data = self.CustomerPortalController._prepare_home_portal_values(counters)

        self.assertNotIn(
            "stock_operations_count",
            data,
            "Should not include stock_operations_count when not requested",
        )

    def test_prepare_home_portal_values_calls_super(self):
        """Verify parent method is called"""
        with patch.object(
            portal.CustomerPortal, "_prepare_home_portal_values"
        ) as mock_super:
            counters = {"stock_operations_count": 0}

            with MockRequest(self.stock_picking_obj.with_user(self.portal_user_1).env):
                self.CustomerPortalController._prepare_home_portal_values(counters)

            mock_super.assert_called_once_with(counters)

    def test_prepare_stock_operations_rendering_values(self):
        """Comprehensive test for _prepare_stock_operations_portal_rendering_values"""

        self.config_obj.create(
            {
                "portal_visible_operation_ids": self.operation_types.ids,
            }
        ).execute()

        self._get_picking()

        test_cases = [
            {},
            {"sortby": "name"},
            {"filterby": "outgoing"},
            {
                "date_begin": (datetime.now() - relativedelta(days=1)).strftime(
                    "%Y-%m-%d"
                ),
                "date_end": datetime.now().strftime("%Y-%m-%d"),
            },
        ]

        for case in test_cases:
            with MockRequest(self.stock_picking_obj.with_user(self.portal_user_1).env):
                controller = self.CustomerPortalController
                result = controller._prepare_stock_operations_portal_rendering_values(
                    **case
                )

            self.assertIn("stock_operation_ids", result)
            self.assertIn("pager", result)
            self.assertIn("searchbar_filters", result)
            self.assertIn("searchbar_sortings", result)

            if "sortby" in case:
                self.assertEqual(result["sortby"], case["sortby"])
            else:
                self.assertEqual(result["sortby"], "date")

            if "filterby" in case:
                self.assertEqual(
                    result["searchbar_filters"][case["filterby"]]["domain"],
                    [("picking_type_id.code", "=", case["filterby"])],
                )

    def test_portal_stock_operation_page_session_branch(self):
        """Cover the `if session_obj_date != today:` branch on first access."""
        pickings = self._get_picking()
        picking = pickings[0]
        self.config_obj.create(
            {
                "portal_visible_operation_ids": self.operation_types.ids,
            }
        ).execute()

        picking._portal_ensure_token()
        token = picking.access_token
        base = picking.get_base_url()
        url = f"{base}/my/stock_operations/{picking.id}?access_token={token}"

        response = self.opener.get(url)
        self.assertEqual(
            response.status_code, 200, "First GET with access_token should return 200."
        )

        response2 = self.opener.get(url)
        self.assertEqual(
            response2.status_code,
            200,
            "Second GET with same token should also return 200.",
        )
