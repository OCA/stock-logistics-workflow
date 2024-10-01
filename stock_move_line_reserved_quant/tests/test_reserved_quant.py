# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMoveLineReservedQuant(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.customers = cls.env.ref("stock.stock_location_customers")

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "product",
            }
        )

        cls.quant = (
            cls.env["stock.quant"]
            .with_context(inventory_mode=True)
            .create(
                {
                    "product_id": cls.product.id,
                    "inventory_quantity": 3.0,
                    "location_id": cls.stock.id,
                }
            )
        )
        cls.quant._apply_inventory()

    def test_move_line_reserved_quantity(self):
        self.move = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 3.0,
                "location_id": self.stock.id,
                "location_dest_id": self.customers.id,
            }
        )
        self.move._action_confirm()
        self.move._action_assign()

        self.assertEqual(self.quant, self.move.move_line_ids.reserved_quant_id)

        self.move._do_unreserve()
        self.assertFalse(self.move.move_line_ids)
