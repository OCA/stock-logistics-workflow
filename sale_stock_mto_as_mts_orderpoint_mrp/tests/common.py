# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import Form, tagged
from odoo.tests.common import SavepointCase


@tagged("-at_install", "post_install")
class Common(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.seller = cls.env.ref("base.res_partner_1")
        cls.customer = cls.env.ref("base.res_partner_2")
        cls.sale_order_model = cls.env["sale.order"]
        cls.purchase_order_model = cls.env["purchase.order"]
        cls.product_model = cls.env["product.product"]
        cls.setUpClassWarehouse()
        cls.setUpClassProduct()
        cls.setUpClassBom()

    @classmethod
    def setUpClassWarehouse(cls):
        cls.env["stock.warehouse"].search([]).write({"mto_as_mts": True})
        cls.mto_route = cls.env.ref("stock.route_warehouse0_mto")
        cls.buy_route = cls.env.ref("purchase_stock.route_warehouse0_buy")

    @classmethod
    def setUpClassProduct(cls):
        cls.product_bed_with_curtain = cls.product_model.create(
            {
                "name": "BED WITH CURTAINS",
                "type": "product",
                "sale_ok": True,
                "purchase_ok": False,
            }
        )
        cls.tmpl_bed_with_curtain = cls.product_bed_with_curtain.product_tmpl_id
        cls.product_bed_structure = cls.product_model.create(
            {
                "name": "BED STRUCTURE",
                "type": "product",
                "sale_ok": True,
                "purchase_ok": True,
                "seller_ids": [(0, 0, {"name": cls.seller.id, "price": 50.0})],
                "route_ids": [(4, cls.mto_route.id), (4, cls.buy_route.id)],
            }
        )
        cls.product_bed_curtain = cls.product_model.create(
            {
                "name": "BED CURTAIN",
                "type": "product",
                "sale_ok": True,
                "purchase_ok": True,
                "seller_ids": [(0, 0, {"name": cls.seller.id, "price": 10.0})],
                "route_ids": [(4, cls.buy_route.id)],
            }
        )
        cls.product_office_furniture = cls.product_model.create(
            {
                "name": "OFFICE FURNITURE",
                "type": "product",
                "sale_ok": True,
                "purchase_ok": True,
                "seller_ids": [(0, 0, {"name": cls.seller.id, "price": 200.0})],
                "route_ids": [(4, cls.mto_route.id), (4, cls.buy_route.id)],
            }
        )
        cls.tmpl_office_furniture = cls.product_office_furniture.product_tmpl_id
        cls.product_office_chair = cls.product_model.create(
            {
                "name": "OFFICE CHAIR",
                "type": "product",
                "sale_ok": False,
                "purchase_ok": False,
            }
        )
        cls.product_office_desk = cls.product_model.create(
            {
                "name": "OFFICE DESK",
                "type": "product",
                "sale_ok": False,
                "purchase_ok": False,
            }
        )
        cls.product_office_bin = cls.product_model.create(
            {
                "name": "OFFICE BIN",
                "type": "product",
                "sale_ok": False,
                "purchase_ok": True,
                "seller_ids": [(0, 0, {"name": cls.seller.id, "price": 5.0})],
                "route_ids": [(4, cls.mto_route.id), (4, cls.buy_route.id)],
            }
        )
        cls.product_garden_furniture = cls.product_model.create(
            {
                "name": "GARDEN FURNITURE",
                "type": "product",
                "sale_ok": False,
                "purchase_ok": True,
                "seller_ids": [(0, 0, {"name": cls.seller.id, "price": 200.0})],
            }
        )
        cls.tmpl_garden_furniture = cls.product_garden_furniture.product_tmpl_id
        cls.product_garden_chair = cls.product_model.create(
            {
                "name": "GARDEN CHAIR",
                "type": "product",
                "sale_ok": True,
                "purchase_ok": True,
                "seller_ids": [(0, 0, {"name": cls.seller.id, "price": 30.0})],
                "route_ids": [(4, cls.mto_route.id), (4, cls.buy_route.id)],
            }
        )
        cls.product_garden_table = cls.product_model.create(
            {
                "name": "GARDEN TABLE",
                "type": "product",
                "sale_ok": True,
                "purchase_ok": True,
                "seller_ids": [(0, 0, {"name": cls.seller.id, "price": 110.0})],
                "route_ids": [(4, cls.mto_route.id), (4, cls.buy_route.id)],
            }
        )
        cls.tmpl_garden_table = cls.product_garden_table.product_tmpl_id
        cls.product_garden_table_top = cls.product_model.create(
            {
                "name": "GARDEN TABLE TOP",
                "type": "product",
                "sale_ok": True,
                "seller_ids": [(0, 0, {"name": cls.seller.id, "price": 50.0})],
                "route_ids": [(4, cls.mto_route.id), (4, cls.buy_route.id)],
            }
        )
        cls.product_garden_table_leg = cls.product_model.create(
            {
                "name": "GARDEN TABLE LEG",
                "type": "product",
                "sale_ok": False,
                "purchase_ok": False,
            }
        )

    @classmethod
    def setUpClassBom(cls):
        cls.bom_model = cls.env["mrp.bom"]
        cls.bom_bed_with_curtain = cls.bom_model.create(
            {
                "product_tmpl_id": cls.tmpl_bed_with_curtain.id,
                "product_id": cls.product_bed_with_curtain.id,
                "type": "phantom",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {"product_id": cls.product_bed_curtain.id, "product_qty": 2.0},
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_bed_structure.id,
                            "product_qty": 1.0,
                        },
                    ),
                ],
            }
        )
        cls.bom_office_furniture = cls.bom_model.create(
            {
                "product_tmpl_id": cls.tmpl_office_furniture.id,
                "product_id": cls.product_office_furniture.id,
                "type": "phantom",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {"product_id": cls.product_office_desk.id, "product_qty": 1.0},
                    ),
                    (
                        0,
                        0,
                        {"product_id": cls.product_office_chair.id, "product_qty": 2.0},
                    ),
                    (
                        0,
                        0,
                        {"product_id": cls.product_office_bin.id, "product_qty": 3.0},
                    ),
                ],
            }
        )
        cls.bom_garden_table = cls.bom_model.create(
            {
                "product_tmpl_id": cls.tmpl_garden_table.id,
                "product_id": cls.product_garden_table.id,
                "type": "phantom",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_garden_table_leg.id,
                            "product_qty": 4.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_garden_table_top.id,
                            "product_qty": 1.0,
                        },
                    ),
                ],
            }
        )
        cls.bom_garden_furniture = cls.bom_model.create(
            {
                "product_tmpl_id": cls.tmpl_garden_furniture.id,
                "product_id": cls.product_garden_furniture.id,
                "type": "phantom",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {"product_id": cls.product_garden_chair.id, "product_qty": 4.0},
                    ),
                    (
                        0,
                        0,
                        {"product_id": cls.product_garden_table.id, "product_qty": 1.0},
                    ),
                ],
            }
        )

    @classmethod
    def create_sale_order(cls, product):
        order_form = Form(cls.sale_order_model)
        order_form.partner_id = cls.customer
        with order_form.order_line.new() as line:
            line.product_id = product
            line.product_uom_qty = 5.0
        return order_form.save()
