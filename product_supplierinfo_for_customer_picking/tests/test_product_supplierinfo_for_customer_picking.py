# Copyright 2018 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class TestProductSupplierinfoForCustomerPicking(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_model = cls.env["stock.picking"]
        cls.computer_SC234 = cls.env.ref("product.product_product_3")
        cls.deco_addict = cls.env.ref("base.res_partner_2")
        cls.gemini = cls.env.ref("base.res_partner_3")
        cls.deco_addict_olson = cls.env.ref("base.res_partner_address_31")
        cls.company_1 = cls.env.ref("base.main_company")
        cls.company_2 = cls.env["res.company"].create({"name": "Test company 2"})
        cls.computer_SC234.write(
            {
                "customer_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.deco_addict.id,
                            "product_code": "test_deco_addict",
                            "product_name": "test prod name 1",
                            "company_id": cls.company_1,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.gemini.id,
                            "product_code": "test_gemini",
                            "product_name": "test prod name 2",
                            "company_id": cls.company_1,
                        },
                    ),
                ],
            }
        )

    def test_product_supplierinfo_for_customer_picking(self):
        delivery_picking = self.picking_model.new(
            {
                "partner_id": self.deco_addict.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )
        delivery_picking.onchange_picking_type()
        delivery_picking = self.picking_model.create(
            {
                "partner_id": delivery_picking.partner_id.id,
                "picking_type_id": delivery_picking.picking_type_id.id,
                "location_id": delivery_picking.location_id.id,
                "location_dest_id": delivery_picking.location_dest_id.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": self.computer_SC234.partner_ref,
                            "product_id": self.computer_SC234.id,
                            "product_uom": self.computer_SC234.uom_id.id,
                            "product_uom_qty": 1.0,
                        },
                    )
                ],
            }
        )
        move = delivery_picking.move_lines[0]
        self.assertEqual(move.product_customer_code, "test_deco_addict")
        self.assertEqual(move.product_customer_name, "test prod name 1")

        # Test that name stays the same on picking
        # even after a change
        customerinfo = self.computer_SC234.customer_ids.filtered(
            lambda x: x.name == self.deco_addict
        )
        customerinfo.product_code = "different_code"
        customerinfo.product_name = "different name"
        self.assertEqual(move.product_customer_code, "test_deco_addict")
        self.assertEqual(move.product_customer_name, "test prod name 1")

    def test_product_supplierinfo_two_costumers(self):
        delivery_picking = self.picking_model.new(
            {
                "partner_id": self.gemini.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )
        delivery_picking.onchange_picking_type()
        delivery_picking = self.picking_model.create(
            {
                "partner_id": delivery_picking.partner_id.id,
                "picking_type_id": delivery_picking.picking_type_id.id,
                "location_id": delivery_picking.location_id.id,
                "location_dest_id": delivery_picking.location_dest_id.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": self.computer_SC234.partner_ref,
                            "product_id": self.computer_SC234.id,
                            "product_uom": self.computer_SC234.uom_id.id,
                            "product_uom_qty": 1.0,
                        },
                    )
                ],
            }
        )
        move = delivery_picking.move_lines[0]
        self.assertEqual(move.product_customer_code, "test_gemini")
        self.assertEqual(move.product_customer_name, "test prod name 2")

        # Test that customer fields only depend on picking company, not user
        move = move.with_company(self.company_2)
        move._compute_product_customer_code()
        self.assertEqual(move.product_customer_code, "test_gemini")
        self.assertEqual(move.product_customer_name, "test prod name 2")

        move = move.with_company(self.company_1)
        move.company_id = self.company_2
        self.assertEqual(move.product_customer_code, False)
        self.assertEqual(move.product_customer_name, False)

    def test_product_supplierinfo_for_customer_parent_contact(self):
        """Test that supplierinfo_for_customer can also be
        retrieved from the partner's parent"""
        delivery_picking = self.picking_model.new(
            {
                "partner_id": self.deco_addict_olson.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )
        delivery_picking.onchange_picking_type()
        delivery_picking = self.picking_model.create(
            {
                "partner_id": delivery_picking.partner_id.id,
                "picking_type_id": delivery_picking.picking_type_id.id,
                "location_id": delivery_picking.location_id.id,
                "location_dest_id": delivery_picking.location_dest_id.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": self.computer_SC234.partner_ref,
                            "product_id": self.computer_SC234.id,
                            "product_uom": self.computer_SC234.uom_id.id,
                            "product_uom_qty": 1.0,
                        },
                    )
                ],
            }
        )
        move = delivery_picking.move_lines[0]
        self.assertEqual(move.product_customer_code, "test_deco_addict")
        self.assertEqual(move.product_customer_name, "test prod name 1")
