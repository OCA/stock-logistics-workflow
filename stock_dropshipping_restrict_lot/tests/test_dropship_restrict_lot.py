#   Copyright (c) 2024 Groupe Voltaire
#   @author Emilie SOUTIRAS  <emilie.soutiras@groupevoltaire.com>
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestDropshipRestrictLot(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dropshipping_route = cls.env.ref("stock_dropshipping.route_drop_shipping")
        cls.supplier = cls.env["res.partner"].create({"name": "Vendor"})
        cls.customer = cls.env["res.partner"].create({"name": "Customer"})
        # dropship route to be added in test
        cls.dropship_product = cls.env["product.product"].create(
            {
                "name": "Pen drive",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_1").id,
                "lst_price": 100.0,
                "standard_price": 0.0,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "seller_ids": [
                    (0, 0, {"delay": 1, "partner_id": cls.supplier.id, "min_qty": 2.0})
                ],
            }
        )
        cls.dropship_product.product_tmpl_id.tracking = "serial"
        cls.lot_dropship_product = cls.env["product.product"].create(
            {
                "name": "Serial product",
                "tracking": "lot",
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.supplier.id,
                        },
                    )
                ],
                "route_ids": [(4, cls.dropshipping_route.id, 0)],
            }
        )

        # cls.env.user.groups_id |= cls.env.ref("stock.group_stock_user")

    def test_dropship_lot_propagation(self):
        # Required for `route_id` to be visible in the view
        self.env.user.groups_id += self.env.ref("stock.group_adv_location")

        # Create a sales order with a line of 200 PCE incoming shipment,
        # with route_id drop shipping
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.customer
        so_form.payment_term_id = self.env.ref(
            "account.account_payment_term_end_following_month"
        )
        with mute_logger("odoo.tests.common.onchange"):
            # otherwise complains that there's not enough inventory and
            # apparently that's normal according to @jco and @sle
            with so_form.order_line.new() as line:
                line.product_id = self.dropship_product
                line.product_uom_qty = 200
                line.price_unit = 1.00
                line.route_id = self.dropshipping_route

        sale_order_drp_shpng = so_form.save()
        sale_order_drp_shpng.order_line.lot_id = self.env["stock.lot"].create(
            {
                "name": "Seq test DS pdt",
                "product_id": self.dropship_product.id,
            }
        )
        initial_lot = sale_order_drp_shpng.order_line.lot_id
        # Confirm sales order
        sale_order_drp_shpng.action_confirm()

        # Check a quotation was created to a certain vendor
        # and confirm so it becomes a confirmed purchase order
        purchase = self.env["purchase.order"].search(
            [("partner_id", "=", self.supplier.id)]
        )
        self.assertEqual(purchase.state, "draft")
        self.assertEqual(purchase.incoming_picking_count, 0)
        self.assertEqual(sale_order_drp_shpng.delivery_count, 0)
        self.assertEqual(sale_order_drp_shpng.dropship_picking_count, 0)
        self.assertEqual(purchase.dropship_picking_count, 0)

        self.assertNotEqual(purchase.order_line.lot_id, initial_lot)
        self.assertFalse(purchase.order_line.lot_id)
        purchase.button_confirm()

        # Check dropship restrict_lot and purchase lot
        self.assertEqual(purchase.dropship_picking_count, 1)
        purchase.button_approve()
        self.assertTrue(purchase.picking_ids.is_dropship)
        self.assertTrue(purchase.picking_ids.move_ids.restrict_lot_id)
        self.assertTrue(purchase.order_line.lot_id)
        self.assertEqual(purchase.order_line.lot_id, initial_lot)
