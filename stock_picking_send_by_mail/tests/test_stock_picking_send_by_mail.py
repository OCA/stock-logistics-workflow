# Copyright 2017 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestStockPickingSendByMail(BaseCommon):
    _test_user_groups = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        cls.location_id = cls.env.ref("stock.stock_location_stock")
        cls.location_destination_id = cls.env.ref("stock.stock_location_customers")
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type.id,
                "location_id": cls.location_id.id,
                "location_dest_id": cls.location_destination_id.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "uom_id": cls.product.uom_id.id,
                            "location_id": cls.location_id.id,
                            "location_dest_id": cls.location_destination_id.id,
                        },
                    )
                ],
            }
        )

    def test_send_mail(self):
        self.picking.action_confirm()
        self.picking.action_assign()
        result = self.picking.action_picking_send()
        self.assertEqual(result["name"], "Compose Email")
