# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestStockPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product = cls.env.ref("product.product_delivery_01")
        cls.product2 = cls.product.copy()
        # add qty to product 2
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product2.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "quantity": 100.0,
            }
        )
        so_vals = {
            "partner_id": cls.partner.id,
            "partner_invoice_id": cls.partner.id,
            "partner_shipping_id": cls.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": cls.product.name,
                        "product_id": cls.product.id,
                        "product_uom_qty": 5.0,
                        "product_uom": cls.product.uom_id.id,
                        "price_unit": cls.product.list_price,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": cls.product2.name,
                        "product_id": cls.product2.id,
                        "product_uom_qty": 13.0,
                        "product_uom": cls.product2.uom_id.id,
                        "price_unit": cls.product2.list_price,
                    },
                ),
            ],
        }
        cls.so = cls.env["sale.order"].create(so_vals)

    def _do_confirm_and_deliver(self, so):
        # confirm our standard so, check the picking
        so.action_confirm()
        # deliver completely
        picking = so.picking_ids
        picking.action_confirm()
        # cancel one line, that one wont be returned
        p1_moves = picking.move_ids.filtered(lambda x: x.product_id == self.product)
        p1_moves.write({"quantity": 5.0})
        p2_moves = picking.move_ids.filtered(lambda x: x.product_id == self.product2)
        p2_moves._action_cancel()
        picking.button_validate()
        return picking

    def test_return_and_recreate(self):
        # confirm our standard so and deliver
        picking = self._do_confirm_and_deliver(self.so)
        picking.action_revert_recreate()

        # we have the original shipment, return and the duplicated, by creation order
        so_pickings = self.so.picking_ids.sorted(key=lambda x: x.id)
        self.assertEqual(len(so_pickings), 3)

        # All pickings same quantity
        so_product_moves = so_pickings.move_ids.filtered(
            lambda x: x.product_id == self.product
        )
        self.assertEqual(so_product_moves.mapped("product_uom_qty"), [5.0, 5.0, 5.0])

        # check return destination location
        self.assertEqual(so_pickings[1].move_ids.location_dest_id.name, "Stock")

        # check duplicate destination location
        self.assertEqual(so_pickings[2].move_ids.location_dest_id.name, "Customers")
        self.assertEqual(so_pickings[2].state, "assigned")

    def test_exemption_is_raised_on_existing_returns(self):
        # confirm our standard so and deliver
        picking = self._do_confirm_and_deliver(self.so)
        # Create return picking
        return_wiz = (
            self.env["stock.return.picking"]
            .with_context(active_id=picking.id, active_model="stock.picking")
            .create({})
        )
        return_wiz = self.env["stock.return.picking"].create({})
        return_wiz.picking_id = picking
        return_wiz.product_return_moves.quantity = 5.0
        return_wiz.create_returns()
        # check error is raised when returning & recreating
        with self.assertRaises(UserError):
            picking.action_revert_recreate()

    def test_exemption_is_raised_on_chained_moves(self):
        # confirm our standard so, check the picking
        self.so.action_confirm()
        # deliver completely
        picking = self.so.picking_ids
        picking.action_confirm()
        self.env.ref("stock.warehouse0").delivery_steps = "pick_pack_ship"
        picking = self.so.picking_ids
        picking.move_ids.write({"quantity": 5.0})
        picking.button_validate()
        # check error is raised when returning & recreating
        with self.assertRaises(UserError):
            picking.action_revert_recreate()
