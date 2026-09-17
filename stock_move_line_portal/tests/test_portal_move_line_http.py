from odoo.tests import tagged

from .common import StockMoveLinePortalHttpCommon


@tagged("post_install", "-at_install")
class TestPortalMoveLineHttp(StockMoveLinePortalHttpCommon):
    def test_my_move_operations_route(self):
        self.authenticate("portal_a", "portal_a")
        response = self.url_open("/my/move_operations")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Producto ML 1", response.content)

    def test_single_operation_route_access(self):
        self.authenticate("portal_a", "portal_a")
        response = self.url_open(f"/my/move_operations/{self.move_line_in_a.id}")

        self.assertEqual(response.status_code, 200)

    def test_single_operation_route_access_denied(self):
        self.authenticate("portal_a", "portal_a")
        response = self.url_open(
            f"/my/move_operations/{self.move_line_in_b.id}", allow_redirects=False
        )

        self.assertIn(response.status_code, (302, 303))
        self.assertIn("/my", response.headers.get("Location", ""))
