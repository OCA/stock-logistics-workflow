# Copyright 2023 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestProductCustomerinfoPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.src_location = cls.env.ref("stock.stock_location_stock")
        cls.dest_location = cls.env.ref("stock.stock_location_customers")
        cls.computer_SC234 = cls.env["product.product"].create(
            {
                "name": "Desk Combination",
                "type": "consu",
                "list_price": 450.0,
                "default_code": "FURN_7800",
            }
        )
        cls.agrolait = cls.env["res.partner"].create(
            {
                "name": "Acme Corporation",
                "is_company": True,
                "street": "77 Santa Barbara Rd",
                "city": "Pleasant Hill",
                "state_id": cls.env.ref("base.state_us_5").id,
                "zip": "94523",
                "phone": "(603)-996-3829",
                "email": "acme_corp@yourcompany.example.com",
                "website": "http://www.acme-example-company.com",
                "vat": "US12345673",
            }
        )
        cls.gemini = cls.env["res.partner"].create(
            {
                "name": "Gemini Furniture",
                "is_company": True,
                "street": "Via Industria 21",
                "city": "Serravalle",
                "state_id": cls.env.ref("base.sm").id,
                "zip": "47899",
                "phone": "+378 0549 885555",
                "email": "gemini_furniture@fake.geminifurniture.com",
                "website": "http://www.gemini-furniture.com/",
                "vat": "SM12345",
            }
        )
        cls.computer_SC234.write(
            {
                "customer_ids": [
                    Command.create(
                        {
                            "partner_id": cls.agrolait.id,
                            "product_code": "test_agrolait",
                        },
                    ),
                    Command.create(
                        {
                            "partner_id": cls.gemini.id,
                            "product_code": "test_gemini",
                        },
                    ),
                ],
            }
        )

    @classmethod
    def _create_delivery_picking(cls, partner, **kwargs):
        delivery_picking = cls.env["stock.picking"].new(
            {
                "partner_id": partner.id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
            }
        )
        delivery_picking._onchange_picking_type()
        vals = {
            "partner_id": delivery_picking.partner_id.id,
            "picking_type_id": delivery_picking.picking_type_id.id,
            "location_id": cls.src_location.id,
            "location_dest_id": cls.dest_location.id,
            "move_ids": [
                Command.create(
                    {
                        "product_id": cls.computer_SC234.id,
                        "product_uom": cls.computer_SC234.uom_id.id,
                        "product_uom_qty": 1.0,
                        "location_id": cls.src_location.id,
                        "location_dest_id": cls.dest_location.id,
                    },
                )
            ],
        }
        vals.update(kwargs)
        return cls.env["stock.picking"].create(vals)

    def test_product_customerinfo_picking(self):
        delivery_picking = self._create_delivery_picking(self.agrolait)
        move = delivery_picking.move_ids[:1]
        self.assertEqual(move.product_customer_code, "test_agrolait")

    def test_product_customerinfo_two_costumers(self):
        delivery_picking = self._create_delivery_picking(self.gemini)
        move = delivery_picking.move_ids[:1]
        self.assertEqual(move.product_customer_code, "test_gemini")

    def test_product_customerinfo_variant_precedence(self):
        self.env["product.customerinfo"].create(
            {
                "partner_id": self.agrolait.id,
                "product_tmpl_id": self.computer_SC234.product_tmpl_id.id,
                "product_id": self.computer_SC234.id,
                "product_code": "test_agrolait_variant",
                "product_name": "Variant name for agrolait",
            }
        )
        delivery_picking = self._create_delivery_picking(self.agrolait)
        move = delivery_picking.move_ids[:1]
        self.assertEqual(move.product_customer_code, "test_agrolait_variant")
        self.assertEqual(move.product_customer_name, "Variant name for agrolait")

    def test_product_customerinfo_no_partner(self):
        delivery_picking = self._create_delivery_picking(
            self.agrolait, partner_id=False
        )
        move = delivery_picking.move_ids[:1]
        self.assertFalse(move.product_customer_code)
