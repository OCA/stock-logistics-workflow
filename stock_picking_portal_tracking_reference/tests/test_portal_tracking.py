# Copyright 2026 Ariel Barreiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo.tests import tagged

from odoo.addons.stock_picking_portal.tests.test_stock_picking_portal import (
    TestStockPickingPortal,
)

TRACKING_REF = "TRACK1234567890"
TRACKING_URL = f"https://track.example.com/{TRACKING_REF}"


@tagged("post_install", "-at_install")
class TestPortalTracking(TestStockPickingPortal):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.delivery_product = cls.env["product.product"].create(
            {"name": "Delivery Charges", "type": "service"}
        )
        cls.carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Test Carrier",
                "delivery_type": "fixed",
                "product_id": cls.delivery_product.id,
                "tracking_url": "https://track.example.com/<shipmenttrackingnumber>",
            }
        )
        cls.carrier_without_url = cls.env["delivery.carrier"].create(
            {
                "name": "Untracked Carrier",
                "delivery_type": "fixed",
                "product_id": cls.delivery_product.id,
            }
        )

    def _enable_portal_operations(self):
        self.config_obj.create(
            {"portal_visible_operation_ids": self.operation_types.ids}
        ).execute()

    def _get_tracking_anchor(self, body):
        for anchor in re.findall(r"<a\s[^>]*>", body):
            if TRACKING_URL in anchor:
                return anchor
        return ""

    def _get_tracked_picking(self, carrier=None):
        picking = self._get_picking()[0]
        picking.write(
            {
                "carrier_id": (carrier or self.carrier).id,
                "carrier_tracking_ref": TRACKING_REF,
            }
        )
        picking._portal_ensure_token()
        return picking

    def test_carrier_tracking_url_is_computed(self):
        """The fixed carrier substitutes the tracking reference in its URL"""
        picking = self._get_tracked_picking()
        self.assertEqual(
            picking.carrier_tracking_url,
            TRACKING_URL,
            msg="The tracking URL should be built from the carrier template",
        )

    def test_document_page_shows_tracking_link(self):
        """The operation page renders the tracking reference as a button"""
        picking = self._get_tracked_picking()
        self._enable_portal_operations()
        self.authenticate(self.portal_user_1.login, self.portal_user_1.login)
        response = self.opener.get(
            f"{picking.get_base_url()}/my/stock_operations/{picking.id}"
            f"?access_token={picking.access_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('name="div_tracking"', response.text)
        self.assertIn(TRACKING_REF, response.text)
        self.assertIn(
            "btn",
            self._get_tracking_anchor(response.text),
            msg="The tracking reference should link to the tracking URL as a button",
        )

    def test_document_page_without_tracking_ref(self):
        """The tracking block is omitted when no tracking reference is set"""
        picking = self._get_picking()[0]
        picking._portal_ensure_token()
        self._enable_portal_operations()
        self.authenticate(self.portal_user_1.login, self.portal_user_1.login)
        response = self.opener.get(
            f"{picking.get_base_url()}/my/stock_operations/{picking.id}"
            f"?access_token={picking.access_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('name="div_tracking"', response.text)

    def test_document_page_without_tracking_url(self):
        """A carrier without a tracking URL renders the reference as plain text"""
        picking = self._get_tracked_picking(carrier=self.carrier_without_url)
        self._enable_portal_operations()
        self.authenticate(self.portal_user_1.login, self.portal_user_1.login)
        response = self.opener.get(
            f"{picking.get_base_url()}/my/stock_operations/{picking.id}"
            f"?access_token={picking.access_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('name="div_tracking"', response.text)
        self.assertIn(TRACKING_REF, response.text)
        self.assertNotIn(
            "Untracked Carrier",
            response.text,
            msg="The carrier name is not part of the tracking information",
        )
        self.assertNotIn(TRACKING_URL, response.text)

    def test_list_page_shows_tracking_link(self):
        """The operations list renders the tracking link without carrier access"""
        picking = self._get_tracked_picking()
        self._enable_portal_operations()
        self.assertFalse(
            self.env["delivery.carrier"]
            .with_user(self.portal_user_1)
            .browse(self.carrier.id)
            .has_access("read"),
            msg="Portal users are not supposed to read delivery carriers",
        )
        self.authenticate(self.portal_user_1.login, self.portal_user_1.login)
        response = self.opener.get(f"{picking.get_base_url()}/my/stock_operations")
        self.assertEqual(response.status_code, 200)
        self.assertIn(picking.name, response.text)
        self.assertIn(
            "btn",
            self._get_tracking_anchor(response.text),
            msg="The tracking reference should link to the tracking URL as a button",
        )
