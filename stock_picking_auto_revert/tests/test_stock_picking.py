# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestStockPicking(TransactionCase):
    def setUp(self):
        super(TestStockPicking, self).setUp()
        self.Picking = self.env["stock.picking"]
        self.picking_type_in = self.env.ref("stock.picking_type_in")
        self.picking_type_out = self.env.ref("stock.picking_type_out")
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.customer_location = self.env.ref("stock.stock_location_customers")
        self.stock_location = self.env.ref("stock.stock_location_stock")

    def test_return_and_recreate(self):
        """ Testing normal flow"""
        self.partner = self.env.ref("base.res_partner_1")
        self.product = self.env.ref("product.product_delivery_01")

        # ensure we can deliver
        values = {
            "product_id": self.product.id,
            "new_quantity": 5.0,
        }
        wizard = self.env["stock.change.product.qty"].create(values)
        wizard.change_product_qty()

        so_vals = {
            "partner_id": self.partner.id,
            "partner_invoice_id": self.partner.id,
            "partner_shipping_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product.name,
                        "product_id": self.product.id,
                        "product_uom_qty": 5.0,
                        "product_uom": self.product.uom_id.id,
                        "price_unit": self.product.list_price,
                    },
                )
            ],
            "pricelist_id": self.env.ref("product.list0").id,
        }
        so = self.env["sale.order"].create(so_vals)

        # confirm our standard so, check the picking
        so.action_confirm()

        # deliver completely
        picking = so.picking_ids

        # Validate picking and recreate
        picking.action_assign()
        operations = picking.mapped("move_ids_without_package.move_line_ids")
        for op in operations:
            op.qty_done = op.product_qty
        picking.button_validate()
        picking.action_revert_recreate()

        # we have the original shipment and the return and the
        # duplicated
        self.assertEqual(len(so.picking_ids), 3)

        # All pickings same quantity
        self.assertEqual(
            so.mapped("picking_ids.move_lines.product_uom_qty"),
            [5.0, 5.0, 5.0],
        )

        # check return destination location
        self.assertEqual(
            so.picking_ids[1].mapped("move_lines.location_dest_id.name"),
            ["Stock"],
        )

        # check duplicate destination location
        self.assertEqual(
            so.picking_ids[0].mapped("move_lines.location_dest_id.name"),
            ["Customers"],
        )

        # resulting picking status and quantity check
        self.assertEqual(so.picking_ids[0].state, "draft")
        self.assertEqual(
            so.picking_ids[0]
            .mapped("move_ids_without_package")
            .product_uom_qty,
            5.0,
        )

        def test_no_availability_no_party(self):
            """ Testing no availability checks"""
            component = self.env["product.product"].create(
                {"name": "component", "type": "product"}
            )

            # Receive
            picking_in = self.Picking.create(
                {
                    "picking_type_id": self.picking_type_in.id,
                    "location_id": self.supplier_location.id,
                    "location_dest_id": self.customer_location.id,
                    "move_lines": [
                        (
                            0,
                            0,
                            {
                                "name": "move 1",
                                "product_id": component.id,
                                "product_uom_qty": 5.0,
                                "product_uom": component.uom_id.id,
                                "location_id": self.supplier_location.id,
                                "location_dest_id": self.stock_location.id,
                            },
                        )
                    ],
                }
            )
            picking.action_assign()
            picking.button_validate()

            self.Picking.create(
                {
                    "picking_type_id": self.picking_type_out.id,
                    "location_id": self.supplier_location.id,
                    "location_dest_id": self.customer_location.id,
                    "move_lines": [
                        (
                            0,
                            0,
                            {
                                "name": "move 1",
                                "product_id": component.id,
                                "product_uom_qty": 5.0,
                                "product_uom": component.uom_id.id,
                                "location_id": self.stock_location.id,
                                "location_dest_id": self.customer_location.id,
                            },
                        )
                    ],
                }
            )
            with self.assertRaises(UserError):
                picking_in.action_revert_recreate()
