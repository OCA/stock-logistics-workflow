# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestStockPickingProductAssortment(TransactionCase):
    def setUp(self):
        super().setUp()
        self.filter_obj = self.env["ir.filters"]
        self.product_obj = self.env["product.template"]
        self.stock_picking_obj = self.env["stock.picking"]
        self.pick_type_out = self.env.ref("stock.picking_type_out")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.customers_location = self.env.ref("stock.stock_location_customers")
        self.product_category = self.env["product.category"].create(
            {"name": "Test Product category"}
        )
        self.partner_1 = self.env["res.partner"].create({"name": "Test partner 1"})
        self.partner_2 = self.env["res.partner"].create({"name": "Test partner 2"})
        self.product_1 = self.product_obj.create(
            {
                "name": "Test product 1",
                "sale_ok": True,
                "type": "product",
                "categ_id": self.product_category.id,
                "description_sale": "Test Description Sale",
            }
        )
        self.product_2 = self.product_obj.create(
            {
                "name": "Test product 2",
                "sale_ok": True,
                "type": "product",
                "categ_id": self.product_category.id,
                "description_sale": "Test Description Sale",
            }
        )

    def test_stock_picking_product_assortment(self):
        assortment_with_whitelist = self.filter_obj.create(
            {
                "name": "Test Assortment 1",
                "model_id": "product.product",
                "domain": [],
                "is_assortment": True,
                "partner_ids": [(4, self.partner_1.id)],
                "whitelist_product_ids": [(4, self.product_1.product_variant_id.id)],
            }
        )
        stock_picking_form = Form(self.stock_picking_obj)
        stock_picking_form.partner_id = self.partner_1
        stock_picking_form.picking_type_id = self.pick_type_out
        stock_picking_form.location_id = self.stock_location
        stock_picking_form.location_dest_id = self.customers_location
        with stock_picking_form.move_ids_without_package.new() as move_id:
            move_id.product_has_both_assortment_id = self.product_1.product_variant_id
            self.assertEquals(move_id.product_id, self.product_1.product_variant_id)
        stock_picking_1 = stock_picking_form.save()
        self.assertEquals(
            stock_picking_1.whitelist_product_ids,
            assortment_with_whitelist.whitelist_product_ids,
        )
        self.assertTrue(stock_picking_1.has_whitelist)
        self.assertFalse(stock_picking_1.has_blacklist)
        assortment_with_blacklist = self.filter_obj.create(
            {
                "name": "Test Assortment 2",
                "model_id": "product.product",
                "domain": [],
                "is_assortment": True,
                "partner_ids": [(4, self.partner_1.id), (4, self.partner_2.id)],
                "blacklist_product_ids": [(4, self.product_2.product_variant_id.id)],
            }
        )
        stock_picking_form = Form(self.stock_picking_obj)
        stock_picking_form.partner_id = self.partner_1
        stock_picking_form.picking_type_id = self.pick_type_out
        stock_picking_form.location_id = self.stock_location
        stock_picking_form.location_dest_id = self.customers_location
        with stock_picking_form.move_ids_without_package.new() as move_id:
            move_id.product_has_both_assortment_id = self.product_1.product_variant_id
            self.assertEquals(move_id.product_id, self.product_1.product_variant_id)
        stock_picking_2 = stock_picking_form.save()
        self.assertEquals(
            stock_picking_2.whitelist_product_ids,
            assortment_with_whitelist.whitelist_product_ids,
        )
        self.assertEquals(
            stock_picking_2.blacklist_product_ids,
            assortment_with_blacklist.blacklist_product_ids,
        )
        self.assertTrue(stock_picking_2.has_whitelist)
        self.assertTrue(stock_picking_2.has_blacklist)
        stock_picking_form = Form(self.stock_picking_obj)
        stock_picking_form.partner_id = self.partner_2
        stock_picking_form.picking_type_id = self.pick_type_out
        stock_picking_form.location_id = self.stock_location
        stock_picking_form.location_dest_id = self.customers_location
        with stock_picking_form.move_ids_without_package.new() as move_id:
            move_id.product_has_blacklist_assortment_id = (
                self.product_1.product_variant_id
            )
            self.assertEquals(move_id.product_id, self.product_1.product_variant_id)
        stock_picking_3 = stock_picking_form.save()
        self.assertEquals(
            stock_picking_3.blacklist_product_ids,
            assortment_with_blacklist.blacklist_product_ids,
        )
        self.assertFalse(stock_picking_3.has_whitelist)
        self.assertTrue(stock_picking_3.has_blacklist)
