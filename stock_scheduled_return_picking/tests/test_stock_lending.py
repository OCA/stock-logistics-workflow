# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields

from .common import CommonTest


class TestStockLending(CommonTest):
    def _create_delivery(self, qty):
        return self.env["stock.picking"].create(
            {
                # "customer_id": self.customer_a.id,
                "partner_id": self.customer_a.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "return_picking_date": fields.Datetime.now(),
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": self.product_a.display_name,
                            "product_id": self.product_a.id,
                            "product_uom": self.product_a.uom_id.id,
                            "product_uom_qty": qty,
                        },
                    )
                ],
            }
        )

    def test_picking_return(self):

        self._update_quantity_onhand(
            self.product_a, 10, self.env.ref("stock.stock_location_stock")
        )
        self.assertEqual(self.product_a.qty_available, 10)
        picking = self._create_delivery(qty=2)
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(picking.state, "assigned")
        # Validate picking
        for ml in picking.move_lines.mapped("move_line_ids"):
            self.assertEqual(ml.lot_id, self.product_a_lot)
            ml.qty_done = ml.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        # Check picking data
        self.assertTrue(picking.linked_to)
        self.assertEqual(picking.return_picking_date, picking.linked_to.scheduled_date)
        # Check current stock
        self.assertEqual(self.product_a.qty_available, 8)
        self.assertEqual(self.product_a.virtual_available, 10)  # Return
        product_a_lot_stock_qty = self.get_product_qty(
            self.product_a,
            self.env.ref("stock.stock_location_stock"),
            self.product_a_lot,
        )
        self.assertEqual(product_a_lot_stock_qty, 8)
        product_a_lot_customer_qty = self.get_product_qty(
            self.product_a,
            self.env.ref("stock.stock_location_customers"),
            self.product_a_lot,
        )
        self.assertEqual(product_a_lot_customer_qty, 2)
        # Validate return
        picking.linked_to.action_assign()
        self.assertEqual(picking.linked_to.state, "assigned")
        for ml in picking.linked_to.move_lines.mapped("move_line_ids"):
            self.assertEqual(ml.lot_id, self.product_a_lot)
            ml.qty_done = ml.product_uom_qty
        picking.linked_to.button_validate()
        # Check current stock
        self.assertEqual(picking.linked_to.state, "done")
        self.assertEqual(self.product_a.qty_available, 10)
        product_a_lot_stock_qty = self.get_product_qty(
            self.product_a,
            self.env.ref("stock.stock_location_stock"),
            self.product_a_lot,
        )
        self.assertEqual(product_a_lot_stock_qty, 10)
        product_a_lot_customer_qty = self.get_product_qty(
            self.product_a,
            self.env.ref("stock.stock_location_customers"),
            self.product_a_lot,
        )
        self.assertEqual(product_a_lot_customer_qty, 0)
