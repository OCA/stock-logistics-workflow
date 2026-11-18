# Copyright 2023 ForgeFlow <http://www.forgeflow.com>
# Copyright 2025 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
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
        # Delivery address child of agrolait — code is on the parent only
        cls.agrolait_delivery = cls.env["res.partner"].create(
            {
                "name": "Agrolait Delivery Address",
                "parent_id": cls.agrolait.id,
                "type": "delivery",
            }
        )
        cls.wh_main = cls.env.ref("stock.warehouse0")
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
                (
                    0,
                    0,
                    {
                        "name": cls.computer_SC234.partner_ref,
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
        move = fields.first(delivery_picking.move_ids)
        self.assertEqual(move.product_customer_code, "test_agrolait")

    def test_product_customerinfo_two_costumers(self):
        delivery_picking = self._create_delivery_picking(self.gemini)
        move = fields.first(delivery_picking.move_ids)
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
        move = fields.first(delivery_picking.move_ids)
        self.assertEqual(move.product_customer_code, "test_agrolait_variant")
        self.assertEqual(move.product_customer_name, "Variant name for agrolait")

    def test_product_customerinfo_no_partner(self):
        delivery_picking = self._create_delivery_picking(
            self.agrolait, partner_id=False
        )
        move = fields.first(delivery_picking.move_ids)
        self.assertFalse(move.product_customer_code)

    def test_report_product_display_name(self):
        delivery_picking = self._create_delivery_picking(self.agrolait)
        move = fields.first(delivery_picking.move_ids)
        self.assertEqual(
            move._get_report_product_display_name(),
            f"[test_agrolait] {self.computer_SC234.name}",
        )
        no_partner_picking = self._create_delivery_picking(
            self.agrolait, partner_id=False
        )
        no_partner_move = fields.first(no_partner_picking.move_ids)
        self.assertEqual(
            no_partner_move._get_report_product_display_name(),
            self.computer_SC234.display_name,
        )

    def test_delivery_slip_customer_code(self):
        delivery_picking = self._create_delivery_picking(self.agrolait)
        delivery_picking.action_confirm()
        report = self.env["ir.actions.report"]._render_qweb_html(
            "stock.report_deliveryslip", delivery_picking.ids
        )[0]
        self.assertIn("[test_agrolait]", report.decode())
        self.assertNotIn(self.computer_SC234.default_code, report.decode())

    def test_delivery_slip_customer_code_done(self):
        delivery_picking = self._create_delivery_picking(self.agrolait)
        delivery_picking.action_confirm()
        self.env["stock.quant"]._update_available_quantity(
            self.computer_SC234, self.src_location, 1.0
        )
        delivery_picking.action_assign()
        for move in delivery_picking.move_ids:
            move.quantity = move.product_uom_qty
            move.picked = True
        delivery_picking._action_done()
        self.assertEqual(delivery_picking.state, "done")
        report = self.env["ir.actions.report"]._render_qweb_html(
            "stock.report_deliveryslip", delivery_picking.ids
        )[0]
        self.assertIn("[test_agrolait]", report.decode())
        self.assertNotIn(self.computer_SC234.default_code, report.decode())

    def test_product_customerinfo_delivery_address(self):
        """Code defined on the parent partner resolves for a delivery address."""
        delivery_picking = self.env["stock.picking"].create(
            {
                "partner_id": self.agrolait_delivery.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
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

    def test_product_customerinfo_consignment_receipt(self):
        """Receipt into a consignment WH uses the warehouse partner as fallback."""
        # Warehouse whose partner_id points to agrolait (consignment scenario)
        self.wh_main.partner_id = self.agrolait
        vendor = self.env["res.partner"].create({"name": "Test Vendor"})
        wh_stock = self.wh_main.lot_stock_id
        receipt = self.env["stock.picking"].create(
            {
                "partner_id": vendor.id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": wh_stock.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.computer_SC234.partner_ref,
                            "product_id": self.computer_SC234.id,
                            "product_uom": self.computer_SC234.uom_id.id,
                            "product_uom_qty": 1.0,
                            "location_id": self.env.ref(
                                "stock.stock_location_suppliers"
                            ).id,
                            "location_dest_id": wh_stock.id,
                        },
                    )
                ],
            }
        )
        move = receipt.move_ids[0]
        move._compute_product_customer_code()
        # Vendor has no customerinfo; warehouse partner (agrolait) has one
        self.assertEqual(move.product_customer_code, "test_agrolait")

    def test_product_customerinfo_consignment_delivery(self):
        """Delivery from a consignment WH uses the warehouse partner as fallback."""
        # Warehouse whose partner_id points to agrolait (consignment scenario)
        self.wh_main.partner_id = self.agrolait
        end_customer = self.env["res.partner"].create({"name": "End Customer"})
        wh_stock = self.wh_main.lot_stock_id
        delivery = self.env["stock.picking"].create(
            {
                "partner_id": end_customer.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": wh_stock.id,
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
                            "location_id": wh_stock.id,
                            "location_dest_id": self.dest_location.id,
                        },
                    )
                ],
            }
        )
        move = delivery.move_ids[0]
        move._compute_product_customer_code()
        # End customer has no customerinfo; warehouse partner (agrolait) has one
        self.assertEqual(move.product_customer_code, "test_agrolait")
