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
        # Product with two variants for variant-specific customerinfo tests
        cls.attr = cls.env["product.attribute"].create({"name": "Size"})
        cls.val_s = cls.env["product.attribute.value"].create(
            {"attribute_id": cls.attr.id, "name": "S"}
        )
        cls.val_m = cls.env["product.attribute.value"].create(
            {"attribute_id": cls.attr.id, "name": "M"}
        )
        cls.variant_tmpl = cls.env["product.template"].create(
            {
                "name": "Test Variant T-Shirt",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attr.id,
                            "value_ids": [(6, 0, [cls.val_s.id, cls.val_m.id])],
                        },
                    )
                ],
            }
        )
        cls.variant_s = cls.variant_tmpl.product_variant_ids.filtered(
            lambda p: cls.val_s
            in p.product_template_attribute_value_ids.product_attribute_value_id
        )
        cls.variant_m = cls.variant_tmpl.product_variant_ids.filtered(
            lambda p: cls.val_m
            in p.product_template_attribute_value_ids.product_attribute_value_id
        )
        # Template-level customerinfo (applies to all variants as fallback)
        cls.variant_tmpl.write(
            {
                "customer_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.agrolait.id,
                            "product_code": "TMPL_AGROLAIT",
                            "product_name": "T-Shirt (Template)",
                        },
                    )
                ]
            }
        )
        # Variant-specific customerinfo (only for variant_s + agrolait)
        cls.env["product.customerinfo"].create(
            {
                "product_tmpl_id": cls.variant_tmpl.id,
                "product_id": cls.variant_s.id,
                "partner_id": cls.agrolait.id,
                "product_code": "VAR_S_AGROLAIT",
                "product_name": "T-Shirt S (Variant)",
            }
        )

    def _create_delivery(self, partner, product):
        return self.env["stock.picking"].create(
            {
                "partner_id": partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.src_location.id,
                "location_dest_id": self.dest_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": product.partner_ref,
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": 1.0,
                            "location_id": self.src_location.id,
                            "location_dest_id": self.dest_location.id,
                        },
                    )
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

    def test_variant_fallback_to_template(self):
        """variant_m has no variant-specific entry → template-level code is used."""
        picking = self._create_delivery(self.agrolait, self.variant_m)
        move = picking.move_ids[0]
        move._compute_product_customer_code()
        self.assertEqual(move.product_customer_code, "TMPL_AGROLAIT")
        self.assertEqual(move.product_customer_name, "T-Shirt (Template)")

    def test_variant_specific_overrides_template(self):
        """
        variant_s has a variant-specific entry
        → it overrides the template-level code.
        """
        picking = self._create_delivery(self.agrolait, self.variant_s)
        move = picking.move_ids[0]
        move._compute_product_customer_code()
        self.assertEqual(move.product_customer_code, "VAR_S_AGROLAIT")
        self.assertEqual(move.product_customer_name, "T-Shirt S (Variant)")

    def test_variant_no_customerinfo_for_other_partner(self):
        """No customerinfo for gemini on variant product → code and name stay empty."""
        picking = self._create_delivery(self.gemini, self.variant_s)
        move = picking.move_ids[0]
        move._compute_product_customer_code()
        self.assertFalse(move.product_customer_code)
        self.assertFalse(move.product_customer_name)
