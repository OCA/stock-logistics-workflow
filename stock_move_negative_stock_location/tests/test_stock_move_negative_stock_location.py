# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import common

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestStockMoveNegativeStockLocation(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env
        cls.product = cls.env.ref("product.product_product_25")
        cls.return_stock_location = cls.env["stock.location"].create(
            {
                "name": "Return Stock Location",
                "usage": "internal",
            }
        )
        cls.env.ref(
            "stock.warehouse0"
        ).return_type_id.default_location_dest_id = cls.return_stock_location

    def test_stock_negative_stock_location(self):
        """Test that the location_id of negative return moves is set to the
        default location_dest_id of the return picking type."""
        location_source = self.env.ref("stock.stock_location_stock")
        location_dest = self.env.ref("stock.stock_location_customers")

        # WH: Stock → Customers
        rule = self.env["stock.rule"].search(
            [
                ("action", "=", "pull"),
                ("picking_type_id", "=", self.env.ref("stock.picking_type_out").id),
                ("location_src_id", "=", location_source.id),
                ("location_dest_id", "=", location_dest.id),
                ("procure_method", "=", "make_to_stock"),
            ]
        )

        move = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": self.product.id,
                "product_uom_qty": -5,
                "product_uom": self.product.uom_id.id,
                "location_id": location_source.id,
                "location_dest_id": location_dest.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "rule_id": rule.id,
            }
        )
        move._action_confirm()
        self.assertEqual(move.location_dest_id, self.return_stock_location)
