# Copyright 2023 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProductCustomerinfoPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.src_location = cls.env.ref("stock.stock_location_stock")
        cls.dest_location = cls.env.ref("stock.stock_location_customers")
        cls.computer_SC234 = cls.env.ref("product.product_product_3")
        cls.agrolait = cls.env.ref("base.res_partner_2")
        cls.gemini = cls.env.ref("base.res_partner_3")
        cls.computer_SC234.write(
            {
                "customer_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.agrolait.id,
                            "product_code": "test_agrolait",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.gemini.id,
                            "product_code": "test_gemini",
                        },
                    ),
                ],
            }
        )

    def test_product_customerinfo_picking(self):
        delivery_picking = self.env["stock.picking"].new(
            {
                "partner_id": self.agrolait.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )
        delivery_picking._onchange_picking_type()
        delivery_picking = self.env["stock.picking"].create(
            {
                "partner_id": delivery_picking.partner_id.id,
                "picking_type_id": delivery_picking.picking_type_id.id,
                "location_id": self.src_location.id,
                "location_dest_id": self.dest_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.computer_SC234.partner_ref,
                            "product_id": self.computer_SC234.id,
                            "product_uom": self.computer_SC234.uom_id.id,
                            "product_uom_qty": 1.0,
                            "location_id": self.src_location.id,
                            "location_dest_id": self.dest_location.id,
                        },
                    )
                ],
            }
        )
        move = delivery_picking.move_ids[0]
        move._compute_product_customer_code()
        self.assertEqual(move.product_customer_code, "test_agrolait")

    def test_product_customerinfo_two_costumers(self):
        delivery_picking = self.env["stock.picking"].new(
            {
                "partner_id": self.gemini.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )
        delivery_picking._onchange_picking_type()
        delivery_picking = self.env["stock.picking"].create(
            {
                "partner_id": delivery_picking.partner_id.id,
                "picking_type_id": delivery_picking.picking_type_id.id,
                "location_id": self.src_location.id,
                "location_dest_id": self.dest_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.computer_SC234.partner_ref,
                            "product_id": self.computer_SC234.id,
                            "product_uom": self.computer_SC234.uom_id.id,
                            "product_uom_qty": 1.0,
                            "location_id": self.src_location.id,
                            "location_dest_id": self.dest_location.id,
                        },
                    )
                ],
            }
        )
        move = delivery_picking.move_ids[0]
        move._compute_product_customer_code()
        self.assertEqual(move.product_customer_code, "test_gemini")
