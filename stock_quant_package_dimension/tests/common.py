# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import SavepointCase


class TestStockQuantPackageCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.wh.out_type_id.default_location_dest_id = cls.env.ref(
            "stock.stock_location_customers"
        )
        cls.product = cls.env.ref("product.product_delivery_02")
        cls.product.write(
            {
                "weight": 1,
                "packaging_ids": [
                    (0, 0, {"name": "Small Box", "qty": "1", "max_weight": "2"}),
                    (0, 0, {"name": "Box", "qty": "5", "max_weight": "7"}),
                ],
            }
        )
        cls.package = cls.env["stock.quant.package"].create({})
        cls.move = cls.env["stock.move"].create(
            {
                "name": cls.product.name,
                "picking_type_id": cls.wh.out_type_id.id,
                "product_id": cls.product.id,
                "product_uom_qty": 11.0,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.wh.out_type_id.default_location_src_id.id,
                "location_dest_id": cls.wh.out_type_id.default_location_dest_id.id,
                "procure_method": "make_to_stock",
                "group_id": cls.env["procurement.group"].create({"name": "Test"}).id,
            }
        )
        cls.move._assign_picking()
        cls.move.picking_id.action_confirm()
