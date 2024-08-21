# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests.common import Form, TransactionCase


class TestStockAccountFifoReturnOrigin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product_category = cls.env["product.category"].create(
            {
                "name": "Test Category",
                "property_cost_method": "fifo",
                "property_valuation": "real_time",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "categ_id": product_category.id,
                "tracking": "lot",
            }
        )
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")

    def create_picking(self, location, location_dest, picking_type):
        return self.env["stock.picking"].create(
            {
                "location_id": location.id,
                "location_dest_id": location_dest.id,
                "picking_type_id": picking_type.id,
            }
        )

    def create_stock_move(self, picking, product, price=0.0):
        move = self.env["stock.move"].create(
            {
                "name": "Move",
                "product_id": product.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": 5.0,
                "picking_id": picking.id,
            }
        )
        if price:
            move.write({"price_unit": price})
        return move

    def create_stock_move_line(self, move, lot_name=False):
        move_line = self.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "product_id": move.product_id.id,
                "location_id": move.location_id.id,
                "location_dest_id": move.location_dest_id.id,
                "product_uom_id": move.product_uom.id,
                "qty_done": move.product_uom_qty,
                "lot_name": lot_name,
            }
        )
        return move_line

    def test_stock_valuation_fifo_lot(self):
        receipt_picking_1 = self.create_picking(
            self.supplier_location, self.stock_location, self.picking_type_in
        )
        move = self.create_stock_move(receipt_picking_1, self.product, 100)
        self.create_stock_move_line(move, "11111")

        receipt_picking_1.action_confirm()
        receipt_picking_1.action_assign()
        receipt_picking_1._action_done()
        self.assertEqual(move.stock_valuation_layer_ids.value, 500)

        receipt_picking_2 = self.create_picking(
            self.supplier_location, self.stock_location, self.picking_type_in
        )
        move = self.create_stock_move(receipt_picking_2, self.product, 200)
        self.create_stock_move_line(move, "22222")

        receipt_picking_2.action_confirm()
        receipt_picking_2.action_assign()
        receipt_picking_2._action_done()
        self.assertEqual(move.stock_valuation_layer_ids.value, 1000)
        self.assertEqual(self.product.standard_price, 100)

        delivery_picking1 = self.create_picking(
            self.stock_location, self.customer_location, self.picking_type_out
        )
        move = self.create_stock_move(delivery_picking1, self.product)
        move_line = self.create_stock_move_line(move)
        lot_id = self.env["stock.lot"].search(
            [("name", "=", "22222"), ("product_id", "=", self.product.id)]
        )
        move_line.write({"lot_id": lot_id})

        delivery_picking1.action_confirm()
        delivery_picking1.action_assign()
        delivery_picking1._action_done()
        self.assertEqual(abs(move.stock_valuation_layer_ids.value), 1000)

        # Test return delivery
        receipt_picking_3 = self.create_picking(
            self.supplier_location, self.stock_location, self.picking_type_in
        )
        move = self.create_stock_move(receipt_picking_3, self.product, 300)
        self.create_stock_move_line(move, "33333")

        receipt_picking_3.action_confirm()
        receipt_picking_3.action_assign()
        receipt_picking_3._action_done()
        self.assertEqual(move.stock_valuation_layer_ids.value, 1500)

        return_picking_wizard_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=receipt_picking_3.ids,
                active_id=receipt_picking_3.id,
                active_model="stock.picking",
            )
        )
        return_picking_wizard = return_picking_wizard_form.save()
        return_picking_wizard.product_return_moves.write({"quantity": 5})
        return_picking_wizard_action = return_picking_wizard.create_returns()
        return_picking = self.env["stock.picking"].browse(
            return_picking_wizard_action["res_id"]
        )
        return_move = return_picking.move_ids
        return_move.move_line_ids.qty_done = 5
        return_picking.button_validate()
        self.assertEqual(abs(return_move.stock_valuation_layer_ids.value), 1500)
