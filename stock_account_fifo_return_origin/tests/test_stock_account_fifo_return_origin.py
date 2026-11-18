# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests import Form, new_test_user

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
        cls.lot_product = cls.env["product.product"].create(
            {
                "name": "Test Lot Product",
                "categ_id": product_category.id,
                "is_storable": True,
                "tracking": "lot",
                "lot_valuated": True,
            }
        )
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.stock_user = new_test_user(
            cls.env, login="stock_user", groups="stock.group_stock_user"
        )

    def create_lot_receipt_picking(self, price_unit, lot_qtys):
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
                "product_id": self.lot_product.id,
                "product_uom_qty": sum(lot_qtys.values()),
                "product_uom": self.lot_product.uom_id.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "picking_id": picking.id,
                "price_unit": price_unit,
            }
        )
        move._action_confirm()
        move.move_line_ids.unlink()
        for lot_name, qty in lot_qtys.items():
            self.env["stock.move.line"].create(
                {
                    "move_id": move.id,
                    "picking_id": picking.id,
                    "product_id": self.lot_product.id,
                    "location_id": self.supplier_location.id,
                    "location_dest_id": self.stock_location.id,
                    "lot_name": lot_name,
                    "quantity": qty,
                }
            )
        picking.button_validate()
        return picking

    def create_return_picking(self, picking, quantity):
        return_picking_wizard = (
            self.env["stock.return.picking"]
            .with_context(
                active_ids=picking.ids,
                active_id=picking.id,
                active_model="stock.picking",
            )
            .create({})
        )
        return_picking_wizard.product_return_moves.write({"quantity": quantity})
        return_picking_wizard_action = return_picking_wizard.action_create_returns()
        return self.env["stock.picking"].browse(return_picking_wizard_action["res_id"])

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

    def test_stock_account_fifo_return_stock_user(self):
        self.create_receipt_picking(100)
        picking = self.create_receipt_picking(200)
        return_picking = self.create_return_picking(picking, 10)
        return_move = return_picking.move_ids
        return_move.move_line_ids.quantity = 10
        return_picking.with_user(self.stock_user).button_validate()
        self.assertEqual(return_picking.state, "done")
        return_valuation_layer = return_move.stock_valuation_layer_ids[0]
        self.assertEqual(return_valuation_layer.value, -2000)

    def test_stock_account_fifo_return_lot_valuated(self):
        picking = self.create_lot_receipt_picking(100, {"LOT-A": 5, "LOT-B": 5})
        self.create_lot_receipt_picking(300, {"LOT-B": 5})
        lot_b = picking.move_line_ids.lot_id.filtered(lambda lot: lot.name == "LOT-B")
        return_picking = self.create_return_picking(picking, 5)
        return_move = return_picking.move_ids
        return_move.move_line_ids.unlink()
        self.env["stock.move.line"].create(
            {
                "move_id": return_move.id,
                "picking_id": return_picking.id,
                "product_id": self.lot_product.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.supplier_location.id,
                "lot_id": lot_b.id,
                "quantity": 5,
            }
        )
        return_picking.button_validate()
        self.assertEqual(return_move.stock_valuation_layer_ids.value, -500)
        remaining_qtys = {
            svl.lot_id.name: svl.remaining_qty
            for svl in picking.move_ids.stock_valuation_layer_ids
        }
        # Lot B's layer of the origin receipt is used, lot A's is untouched
        self.assertEqual(remaining_qtys, {"LOT-A": 5, "LOT-B": 0})
