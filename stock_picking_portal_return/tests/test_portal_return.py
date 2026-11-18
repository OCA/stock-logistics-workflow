# Copyright 2026 arielbarreiros96 (https://github.com/arielbarreiros96)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import HttpCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestStockPickingPortalReturn(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.portal_user = new_test_user(
            cls.env, login="portal_return_customer", groups="base.group_portal"
        )
        cls.delivery_type = cls.env.ref("stock.picking_type_out")
        cls.env["stock.picking.type"].search([]).portal_visible = False
        (
            cls.delivery_type | cls.delivery_type.return_picking_type_id
        ).portal_visible = True
        cls.product = cls.env["product.product"].create({"name": "Returned product"})

    def setUp(self):
        super().setUp()
        self.authenticate(self.portal_user.login, self.portal_user.login)

    def _create_delivery(self, validate=True, partner=None):
        source = self.delivery_type.default_location_src_id
        customers = self.env.ref("stock.stock_location_customers")
        delivery = self.env["stock.picking"].create(
            {
                "partner_id": (partner or self.portal_user.partner_id).id,
                "picking_type_id": self.delivery_type.id,
                "location_id": source.id,
                "location_dest_id": customers.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "location_id": source.id,
                            "location_dest_id": customers.id,
                        }
                    )
                ],
            }
        )
        delivery.action_confirm()
        if validate:
            self._validate(delivery)
        return delivery

    def _create_return(self, delivery):
        wizard = (
            self.env["stock.return.picking"]
            .with_context(active_id=delivery.id, active_model="stock.picking")
            .create({})
        )
        wizard.action_create_returns_all()
        return delivery.return_ids

    def _validate(self, picking):
        picking.move_ids.write({"quantity": 1, "picked": True})
        picking.button_validate()

    def test_only_delivered_deliveries_are_returnable(self):
        delivery = self._create_delivery()
        self.assertTrue(delivery._portal_is_returnable())
        self.assertFalse(self._create_delivery(validate=False)._portal_is_returnable())
        self.assertFalse(self._create_return(delivery)._portal_is_returnable())

    def test_delivered_operation_offers_the_return_slip(self):
        delivery = self._create_delivery()
        slip_url = delivery.get_portal_url(suffix="/return")
        self.assertIn(slip_url, self.url_open("/my/stock_operations").text)
        self.assertIn(slip_url, self.url_open(delivery.get_portal_url()).text)

    def test_operation_in_preparation_offers_no_return_slip(self):
        delivery = self._create_delivery(validate=False)
        page = self.url_open(delivery.get_portal_url()).text
        self.assertNotIn(delivery.get_portal_url(suffix="/return"), page)

    def test_return_slip_is_rendered(self):
        delivery = self._create_delivery()
        response = self.url_open(delivery.get_portal_url(suffix="/return"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/pdf")

    def test_return_slip_of_an_operation_in_preparation_is_refused(self):
        delivery = self._create_delivery(validate=False)
        response = self.url_open(delivery.get_portal_url(suffix="/return"))
        self.assertEqual(response.status_code, 403)

    def test_return_slip_of_an_unpublished_operation_is_refused(self):
        delivery = self._create_delivery()
        slip_url = delivery.get_portal_url(suffix="/return")
        self.delivery_type.portal_visible = False
        self.assertEqual(self.url_open(slip_url).status_code, 403)

    def test_delivery_and_return_link_to_each_other(self):
        delivery = self._create_delivery()
        delivery_return = self._create_return(delivery)
        delivery_page = self.url_open(delivery.get_portal_url()).text
        return_page = self.url_open(delivery_return.get_portal_url()).text
        self.assertIn(delivery_return.get_portal_url(), delivery_page)
        self.assertIn(delivery.get_portal_url(), return_page)

    def test_unpublished_return_is_listed_without_a_link(self):
        delivery = self._create_delivery()
        delivery_return = self._create_return(delivery)
        delivery_return.picking_type_id.portal_visible = False
        page = self.url_open(delivery.get_portal_url()).text
        self.assertIn(delivery_return.name, page)
        self.assertNotIn(f"/my/stock_operations/{delivery_return.id}?", page)

    def test_return_progress_is_shown_on_the_delivery(self):
        delivery = self._create_delivery()
        delivery_return = self._create_return(delivery)
        self.assertIn("Awaiting arrival", self.url_open(delivery.get_portal_url()).text)
        self._validate(delivery_return)
        self.assertIn("Received", self.url_open(delivery.get_portal_url()).text)

    def test_return_slip_of_another_customer_sends_back_to_the_portal(self):
        other_customer = self.env["res.partner"].create({"name": "Other customer"})
        delivery = self._create_delivery(partner=other_customer)
        response = self.url_open(
            f"/my/stock_operations/{delivery.id}/return", allow_redirects=False
        )
        self.assertIn(response.status_code, (302, 303))
        self.assertTrue(response.headers["Location"].endswith("/my"))
