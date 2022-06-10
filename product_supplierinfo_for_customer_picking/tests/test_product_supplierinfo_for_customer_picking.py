# Copyright 2018 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProductSupplierinfoForCustomerPicking(TransactionCase):
    def setUp(self):
        super(TestProductSupplierinfoForCustomerPicking, self).setUp()
        self.src_location = self.env.ref("stock.stock_location_stock")
        self.dest_location = self.env.ref("stock.stock_location_customers")
        self.product = self.browse_ref("product.product_product_3")
        self.partner = self.browse_ref("base.res_partner_2")
        self.picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.src_location.id,
                "location_dest_id": self.dest_location.id,
            }
        )
        self.move = self.env["stock.move"].create(
            {
                "name": self.product.partner_ref,
                "picking_id": self.picking.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "location_id": self.src_location.id,
                "location_dest_id": self.dest_location.id,
                "product_uom_qty": 1.0,
            }
        )
        self.product.write(
            {
                "customer_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.partner.id,
                            "product_code": "test_agrolait",
                        },
                    )
                ],
            }
        )

    def test_product_supplierinfo_for_customer_picking(self):
        move = self.picking.move_lines[0]
        move._compute_product_customer_code()
        self.assertEqual(move.product_customer_code, "test_agrolait")
