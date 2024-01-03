# Copyright 2017 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestStockPickingSendByMail(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
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
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom": cls.product.uom_id.id,
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
