from odoo.tests import tagged

from odoo.addons.stock_move_line_portal.controllers.portal import CustomerPortal
from odoo.addons.website.tools import MockRequest

from .common import StockMoveLinePortalCommon


@tagged("post_install", "-at_install")
class TestPortalMoveLine(StockMoveLinePortalCommon):
    def setUp(self):
        super().setUp()
        self.controller = CustomerPortal()

    def _with_user_request(self, user):
        return MockRequest(self.env(user=user))

    def test_prepared_move_line_domain(self):
        domain = self.controller._get_prepared_move_line_domain(self.partner_a)
        self.assertEqual(domain, [("picking_partner_id", "=", self.partner_a.id)])

    def test_home_portal_values_count(self):
        with self._with_user_request(self.portal_user_a):
            values = self.controller._prepare_home_portal_values(
                ["move_operations_count"]
            )
        self.assertEqual(values.get("move_operations_count"), 2)

    def test_prepare_portal_rendering_values_isolation(self):
        with self._with_user_request(self.portal_user_a):
            values = self.controller._prepare_move_operations_portal_rendering_values()

        move_lines = values["move_operation_ids"]
        self.assertIn(self.move_line_in_a, move_lines)
        self.assertIn(self.move_line_out_a, move_lines)
        self.assertNotIn(self.move_line_in_b, move_lines)

    def test_rendering_values_filters(self):
        with self._with_user_request(self.portal_user_a):
            val_in = self.controller._prepare_move_operations_portal_rendering_values(
                filterby="incoming"
            )
            moves_in = val_in["move_operation_ids"]
            self.assertIn(self.move_line_in_a, moves_in)
            self.assertNotIn(self.move_line_out_a, moves_in)

            val_out = self.controller._prepare_move_operations_portal_rendering_values(
                filterby="outgoing"
            )
            moves_out = val_out["move_operation_ids"]
            self.assertIn(self.move_line_out_a, moves_out)
            self.assertNotIn(self.move_line_in_a, moves_out)
