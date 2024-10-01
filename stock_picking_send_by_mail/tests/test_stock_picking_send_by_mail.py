# Copyright 2017 Tecnativa <vicent.cubells@tecnativa.com>
# Copyright 2024 Tecnativa Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockPickingSendByMail(TransactionCase):
    def setUp(self):
        super().setUp()
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.env = self.env(context=dict(self.env.context, **DISABLED_MAIL_CONTEXT))
        self.product = self.env["product.product"].create({"name": "Test product"})
        self.location_id = self.env.ref("stock.stock_location_stock")
        self.location_destination_id = self.env.ref("stock.stock_location_customers")
        self.picking_type = self.env.ref("stock.picking_type_out")
        self.picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type.id,
                "location_id": self.location_id.id,
                "location_dest_id": self.location_destination_id.id,
                "move_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_id": self.product.uom_id.id,
                            "location_id": self.location_id.id,
                            "location_dest_id": self.location_destination_id.id,
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
