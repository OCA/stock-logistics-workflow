# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockPickingWarnMessage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # disable tracking test suite wise
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_model = cls.env["res.users"].with_context(no_reset_password=True)
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type_out = cls.warehouse.out_type_id
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env.ref("product.product_product_4")
        cls.warn_msg_parent = "This customer has a warn from parent"
        cls.parent = cls.env["res.partner"].create(
            {
                "name": "Customer with a warn",
                "email": "customer@warn.com",
                "picking_warn": "warning",
                "picking_warn_msg": cls.warn_msg_parent,
            }
        )
        cls.warn_msg = "This customer has a warn"
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Customer with a warn",
                "email": "customer@warn.com",
                "picking_warn": "warning",
                "picking_warn_msg": cls.warn_msg,
            }
        )

    def test_compute_picking_warn_msg(self):
        location_id = self.picking_type_out.default_location_src_id.id
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.picking_type_out.default_location_src_id.id,
                "location_dest_id": self.customer_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 1,
                            "location_id": location_id,
                            "location_dest_id": self.customer_location.id,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(picking.picking_warn_msg, self.warn_msg)

    def test_compute_picking_warn_msg_parent(self):
        self.partner.update({"parent_id": self.parent.id})
        location_id = self.picking_type_out.default_location_src_id.id
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.picking_type_out.default_location_src_id.id,
                "location_dest_id": self.customer_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 1,
                            "location_id": location_id,
                            "location_dest_id": self.customer_location.id,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(
            picking.picking_warn_msg, self.warn_msg_parent + "\n" + self.warn_msg
        )

    def test_compute_picking_warn(self):
        location_id = self.picking_type_out.default_location_src_id.id
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.picking_type_out.default_location_src_id.id,
                "location_dest_id": self.customer_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 1,
                            "location_id": location_id,
                            "location_dest_id": self.customer_location.id,
                        },
                    ),
                ],
            }
        )
        self.partner.update({"picking_warn": "block"})
        self.assertEqual(picking.picking_warn, "block")
        self.partner.update({"picking_warn": "warning"})
        self.assertEqual(picking.picking_warn, "warning")

        # Check that block always overrules warning
        self.partner.update({"parent_id": self.parent.id})
        self.parent.update({"picking_warn": "warning"})
        self.partner.update({"picking_warn": "block"})
        self.assertEqual(picking.picking_warn, "block")
        self.parent.update({"picking_warn": "block"})
        self.partner.update({"picking_warn": "warning"})
        self.assertEqual(picking.picking_warn, "block")

        # We should still see the warning of the partner even when the parent partner
        # has no warning set
        self.parent.update({"picking_warn": "no-message"})
        self.assertEqual(picking.picking_warn, "warning")

        # When both the partner and the parent partner have no message set we expect
        # to see that also in the picking
        self.partner.update({"picking_warn": "no-message"})
        self.assertEqual(picking.picking_warn, "no-message")

        # On the other hand even when the partner has no warning set we still see
        # the one from the parent
        self.parent.update({"picking_warn": "warning"})
        self.assertEqual(picking.picking_warn, "warning")
