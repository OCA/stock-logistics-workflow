from odoo.tests import tagged

from .common import StockMoveLinePortalHttpCommon


@tagged("post_install", "-at_install")
class TestPortalMoveLineHttp(StockMoveLinePortalHttpCommon):
    def test_my_stock_move_line_owner_route(self):
        self.authenticate("portal_a", "portal_a")
        response = self.url_open("/my/stock_move_line/owner")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Producto ML 1", response.content)

    def test_http_route_with_filters(self):
        self.authenticate("portal_a", "portal_a")
        response = self.url_open("/my/stock_move_line/owner?filterby=outgoing")
        self.assertEqual(response.status_code, 200)

    def test_http_route_with_sorting_and_pagination(self):
        self.authenticate("portal_a", "portal_a")
        response = self.url_open("/my/stock_move_line/owner?sortby=date&page=1")
        self.assertEqual(response.status_code, 200)
