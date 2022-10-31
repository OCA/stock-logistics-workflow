# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import SavepointCase


class TestStockPickingProducts(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_model = cls.env["product.template"]
        cls.picking_model = cls.env["stock.picking"]
        cls.move_model = cls.env["stock.move"]

        cls.customer = cls.env.ref("base.res_partner_12")
        cls.product_8 = cls.env.ref("product.product_product_8")
        cls.product_9 = cls.env.ref("product.product_product_9")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")

    def test_stock_picking_product_count(self):
        stock_picking = self.picking_model.create(
            {
                "partner_id": self.customer.id,
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        self.move_model.create(
            {
                "product_id": self.product_8.id,
                "picking_id": stock_picking.id,
                "product_uom_qty": 1.0,
                "name": self.product_8.display_name,
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "product_uom": self.product_8.uom_id.id,
            }
        )
        self.move_model.create(
            {
                "product_id": self.product_9.id,
                "picking_id": stock_picking.id,
                "product_uom_qty": 1.0,
                "name": self.product_9.display_name,
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "product_uom": self.product_9.uom_id.id,
            }
        )

        self.assertEqual(
            sorted(stock_picking.product_ids.ids),
            sorted([self.product_8.id, self.product_9.id]),
        )
        self.assertEqual(stock_picking.product_count, 2)
        # coverage
        stock_picking.action_view_products()
