# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import Command
from odoo.http import Request
from odoo.tests import Form, HttpCase, tagged

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
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.portal_user_1.partner_id
        with so_form.order_line.new() as line:
            line.product_id = self.product_a
        so = so_form.save()
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
