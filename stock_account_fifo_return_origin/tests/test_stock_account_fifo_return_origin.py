# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestStockAccountFifoReturnOrigin(BaseCommon):
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
                "categ_id": product_category.id,
            }
        )
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")

    def create_receipt_picking(self, price_unit):
        picking = self.env["stock.picking"].create(
            {
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "picking_type_id": self.picking_type_in.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": self.product.id,
                "quantity": 10,
                "product_uom": self.product.uom_id.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "picking_id": picking.id,
                "price_unit": price_unit,
            }
        )
        move._action_confirm()
        move._action_assign()
        move.move_line_ids.quantity = 10
        picking.button_validate()
        return picking

    def test_stock_account_fifo_return(self):
        picking = self.create_receipt_picking(100)
        move = picking.move_ids[0]
        stock_valuation_layer = move.stock_valuation_layer_ids[0]
        self.assertEqual(stock_valuation_layer.value, 1000)
        picking = self.create_receipt_picking(200)
        move = picking.move_ids[0]
        stock_valuation_layer = move.stock_valuation_layer_ids[0]
        self.assertEqual(stock_valuation_layer.value, 2000)
        return_picking_wizard_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.id,
                active_model="stock.picking",
            )
        )
        return_picking_wizard = return_picking_wizard_form.save()
        return_picking_wizard.product_return_moves.write({"quantity": 10})
        return_picking_wizard_action = return_picking_wizard.action_create_returns()
        return_picking = self.env["stock.picking"].browse(
            return_picking_wizard_action["res_id"]
        )
        return_move = return_picking.move_ids
        return_move.move_line_ids.quantity = 10
        return_picking.button_validate()
        return_valuation_layer = return_move.stock_valuation_layer_ids[0]
        self.assertEqual(abs(return_valuation_layer.value), 2000)

    def test_create_correction_svl(self):
        self.create_receipt_picking(100)
        picking = self.create_receipt_picking(200)
        picking.action_toggle_is_locked()
        move = picking.move_ids[0]
        move_line = move.move_line_ids[0]
        move_line.quantity = 8
        correction_svl = move.stock_valuation_layer_ids.filtered(
            lambda svl: svl.quantity < 0
        )
        self.assertTrue(correction_svl)
        # Should use receipt's cost (200), not FIFO oldest (100)
        self.assertEqual(correction_svl.value, -400.0)
