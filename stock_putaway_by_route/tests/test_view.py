# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import Form, SavepointCase


class TestPutawayView(SavepointCase):
    def test_view_attrs(self):
        tree = Form(
            self.env["stock.putaway.rule"],
            view=self.env.ref("stock.stock_putaway_list"),
        )
        self.assertFalse(tree._get_modifier("product_id", "readonly"))
        self.assertTrue(tree._get_modifier("product_id", "required"))
        self.assertFalse(tree._get_modifier("category_id", "readonly"))
        self.assertTrue(tree._get_modifier("category_id", "required"))
        self.assertFalse(tree._get_modifier("route_id", "readonly"))
        self.assertTrue(tree._get_modifier("route_id", "required"))

        tree.product_id = self.env["product.product"].search([], limit=1)
        self.assertFalse(tree._get_modifier("product_id", "readonly"))
        self.assertTrue(tree._get_modifier("product_id", "required"))
        self.assertTrue(tree._get_modifier("category_id", "readonly"))
        self.assertFalse(tree._get_modifier("category_id", "required"))
        self.assertTrue(tree._get_modifier("route_id", "readonly"))
        self.assertFalse(tree._get_modifier("route_id", "required"))
        tree.product_id = self.env["product.product"]

        tree.category_id = self.env["product.category"].search([], limit=1)
        self.assertTrue(tree._get_modifier("product_id", "readonly"))
        self.assertFalse(tree._get_modifier("product_id", "required"))
        self.assertFalse(tree._get_modifier("category_id", "readonly"))
        self.assertTrue(tree._get_modifier("category_id", "required"))
        self.assertTrue(tree._get_modifier("route_id", "readonly"))
        self.assertFalse(tree._get_modifier("route_id", "required"))
        tree.category_id = self.env["product.category"]

        tree.route_id = self.env["stock.location.route"].search([], limit=1)
        self.assertTrue(tree._get_modifier("product_id", "readonly"))
        self.assertFalse(tree._get_modifier("product_id", "required"))
        self.assertTrue(tree._get_modifier("category_id", "readonly"))
        self.assertFalse(tree._get_modifier("category_id", "required"))
        self.assertFalse(tree._get_modifier("route_id", "readonly"))
        self.assertTrue(tree._get_modifier("route_id", "required"))
