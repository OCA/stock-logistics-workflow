# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestStockPickingPartnerBlockOut(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env

        cls.customer_a = cls.env["res.partner"].create(
            {
                "name": "Customer A",
            }
        )

        cls.product_8 = cls.env.ref("product.product_product_8")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")

    def test_1(self):
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.customer_a.id,
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "product_id": self.product_8.id,
                "picking_id": picking.id,
                "product_uom_qty": 1.0,
                "name": self.product_8.display_name,
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "product_uom": self.product_8.uom_id.id,
            }
        )

        self.assertEqual(picking.state, "draft")
        picking.action_confirm()

        move.quantity_done = 1

        picking.action_assign()
        self.assertTrue(picking.show_validate)
        self.assertFalse(self.customer_a.picking_block_out)

        self.customer_a.picking_block_out = True

        with self.assertRaisesRegex(
            ValidationError, "You cannot validate this delivery because deliveries"
        ):
            picking._action_done()
