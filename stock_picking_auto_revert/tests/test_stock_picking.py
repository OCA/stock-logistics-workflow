# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import Form
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
            "pricelist_id": cls.env.ref("product.list0").id,
        }
        cls.so = cls.env["sale.order"].create(so_vals)

    def test_return_and_recreate(self):
        # confirm our standard so, check the picking
        self.so.action_confirm()
        # deliver completely
        picking = self.so.picking_ids
        picking.action_confirm()
        # cancel one line, that one wont be returned
        picking = self.so.picking_ids
        picking.move_lines.filtered(lambda x: x.product_id == self.product).write(
            {"quantity_done": 5.0}
        )
        picking.move_lines.filtered(
            lambda x: x.product_id == self.product2
        )._action_cancel()
        picking.button_validate()
        picking.action_revert_recreate()

        # we have the original shipment and the return and the duplicated
        self.assertEqual(len(self.so.picking_ids), 3)

        # All pickings same quantity
        self.assertEqual(
            self.so.mapped("picking_ids.move_lines")
            .filtered(lambda l: l.product_id == self.product)
            .mapped("product_uom_qty"),
            [5.0, 5.0, 5.0],
        )

        # check return destination location
        self.assertEqual(
            sorted(self.so.picking_ids, key=lambda x: x.id)[1].mapped(
                "move_lines.location_dest_id.name"
            ),
            ["Stock"],
        )

        # check duplicate destination location
        self.assertEqual(
            sorted(self.so.picking_ids, key=lambda x: x.id)[2].mapped(
                "move_lines.location_dest_id.name"
            ),
            ["Customers"],
        )
        self.assertEqual(
            sorted(self.so.picking_ids, key=lambda x: x.id)[2].state, "assigned"
        )

    def test_exemption_is_raised_on_existing_returns(self):
        # confirm our standard so, check the picking
        self.so.action_confirm()
        # deliver completely
        picking = self.so.picking_ids
        picking.action_confirm()
        picking = self.so.picking_ids
        picking.move_lines.write({"quantity_done": 5.0})
        picking.move_lines.filtered(
            lambda x: x.product_id == self.product2
        )._action_cancel()
        picking.button_validate()
        # Create return picking
        return_form = Form(self.env["stock.return.picking"])
        return_form.picking_id = picking
        return_wiz = return_form.save()
        return_wiz.product_return_moves.quantity = 5.0
        res = return_wiz.create_returns()
        self.env["stock.picking"].browse(res["res_id"])
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
        picking.move_lines.write({"quantity_done": 5.0})
        picking.button_validate()
        # check error is raised when returning & recreating
        with self.assertRaises(UserError):
            picking.action_revert_recreate()
