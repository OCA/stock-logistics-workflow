# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestCopyQuantity(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.browse_ref("base.res_partner_2")
        self.responsible = self.browse_ref("base.partner_demo")
        self.other_responsible = self.browse_ref("base.res_partner_3")
        self.picking_type_out = self.browse_ref("stock.picking_type_out")
        self.supplier_location = self.browse_ref("stock.stock_location_suppliers")
        self.stock_location = self.browse_ref("stock.stock_location_stock")
        self.product_a = self.env["product.product"].create({"name": "Product A"})
        self.product_b = self.env["product.product"].create({"name": "Product B"})

    def test_responsible_is_added_to_followers(self):
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "responsible_id": self.responsible.id,
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )

        # test create
        self.assertIn(
            self.responsible.id, picking.message_follower_ids.mapped("partner_id").ids
        )

        # test write
        picking.responsible_id = self.other_responsible
        self.assertIn(
            self.other_responsible.id,
            picking.message_follower_ids.mapped("partner_id").ids,
        )
