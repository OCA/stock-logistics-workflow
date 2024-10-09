# Copyright 2017 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2018 Camptocamp SA - Julien Coux
# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestStockSplitPickingCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.src_location = cls.env.ref("stock.stock_location_stock")
        cls.dest_location = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        cls.product_2 = cls.env["product.product"].create({"name": "Test product 2"})
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.src_location.id,
                "location_dest_id": cls.dest_location.id,
            }
        )

        cls.move = cls._create_stock_move(cls.product)
        cls.move_2 = cls._create_stock_move(cls.product_2)

    @classmethod
    def _create_stock_move(cls, product):
        return cls.env["stock.move"].create(
            {
                "name": "/",
                "picking_id": cls.picking.id,
                "product_id": product.id,
                "product_uom_qty": 10,
                "product_uom": product.uom_id.id,
                "location_id": cls.src_location.id,
                "location_dest_id": cls.dest_location.id,
            }
        )
