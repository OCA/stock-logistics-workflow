# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


# `account` is loaded after this module, hence its `res.partner` columns are
# not in the registry yet when tests run at install.
@tagged("post_install", "-at_install")
class TestShippingWeightCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.wh.out_type_id.default_location_dest_id = cls.env.ref(
            "stock.stock_location_customers"
        )
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
                "weight": 1,
                "uom_id": cls.uom_unit.id,
            }
        )
        # "Small Box" contains 1 unit and weights 2
        cls.small_box_uom = cls._create_packaging_uom("Small Box", 1)
        cls.small_box = cls._create_packaging(cls.small_box_uom, 2)
        # "Box" contains 5 units and weights 7
        cls.box_uom = cls._create_packaging_uom("Box", 5)
        cls.box = cls._create_packaging(cls.box_uom, 7)
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.wh.out_type_id.id,
                "location_id": cls.wh.out_type_id.default_location_src_id.id,
                "location_dest_id": cls.wh.out_type_id.default_location_dest_id.id,
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "picking_id": cls.picking.id,
                "product_id": cls.product.id,
                "product_uom_qty": 11.0,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.picking.location_id.id,
                "location_dest_id": cls.picking.location_dest_id.id,
                "procure_method": "make_to_stock",
            }
        )
        cls.picking.action_confirm()

    @classmethod
    def _create_packaging_uom(cls, name, factor):
        return cls.env["uom.uom"].create(
            {
                "name": name,
                "relative_factor": factor,
                "relative_uom_id": cls.uom_unit.id,
            }
        )

    @classmethod
    def _create_packaging(cls, uom, weight):
        return cls.env["product.packaging"].create(
            {"product_id": cls.product.id, "uom_id": uom.id, "weight": weight}
        )
