# Copyright 2017 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestStockPickingSendByMail(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockPickingSendByMail, cls).setUpClass()
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type.id,
                "location_id": cls.picking_type.default_location_src_id.id,
                "location_dest_id": cls.picking_type.default_location_src_id.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom": cls.product.uom_id.id,
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
