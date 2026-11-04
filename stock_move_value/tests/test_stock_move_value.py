# Copyright 2024 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests.common import Form, TransactionCase


class TestStockReturnValueDiscrepancy(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product_category = cls.env["product.category"].create(
            {
                "name": "test category",
                "property_cost_method": "average",
                "property_valuation": "manual_periodic",
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "test product", "categ_id": product_category.id}
        )
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.location_vendor = cls.env.ref("stock.stock_location_suppliers")
        cls.picking_in = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.location_vendor.id,
                "location_dest_id": cls.location_stock.id,
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "name": cls.product.name,
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.location_vendor.id,
                "location_dest_id": cls.location_stock.id,
                "picking_id": cls.picking_in.id,
                "product_uom_qty": 10,
                "quantity_done": 10,
            }
        )

    def create_return_picking(self, origin_pick, returned_qty):
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=origin_pick.ids,
                active_id=origin_pick.id,
                active_model="stock.picking",
            )
        )
        return_modal = stock_return_picking_form.save()
        return_modal.product_return_moves.quantity = returned_qty
        return_modal.location_id = self.location_vendor.id
        return_action = return_modal.create_returns()
        picking = self.env["stock.picking"].browse(return_action["res_id"])
        picking.move_ids[0].quantity_done = returned_qty
        return picking

    def test_picking_return_to_vendor(self):
        self.product.standard_price = 10.0
        self.picking_in._action_done()
        self.assertEqual(self.move.move_value, 100.0)
        self.assertEqual(self.move.move_origin_value, 0.0)
        self.assertEqual(self.move.value_discrepancy, 0.0)
        self.assertFalse(self.move.to_review_discrepancy)
        # Return with no value discrepancy
        return_pick_1 = self.create_return_picking(self.picking_in, 2.0)
        return_pick_1._action_done()
        return_move_1 = return_pick_1.move_ids[0]
        self.assertEqual(return_move_1.move_value, -20.0)
        self.assertEqual(return_move_1.move_origin_value, 20.0)
        self.assertEqual(return_move_1.value_discrepancy, 0.0)
        self.assertFalse(return_move_1.to_review_discrepancy)
        # Return with value discrepancy
        self.product.standard_price = 30.0
        return_pick_2 = self.create_return_picking(self.picking_in, 5.0)
        return_pick_2._action_done()
        return_move_2 = return_pick_2.move_ids[0]
        self.assertEqual(return_move_2.move_value, -150.0)
        self.assertEqual(return_move_2.move_origin_value, 50.0)
        self.assertEqual(return_move_2.value_discrepancy, -100.0)
        self.assertTrue(return_move_2.to_review_discrepancy)
