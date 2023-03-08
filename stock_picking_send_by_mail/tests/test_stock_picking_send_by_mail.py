# Copyright 2017 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import common


class TestStockPickingSendByMail(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockPickingSendByMail, cls).setUpClass()
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.customer = cls.env["res.partner"].create(
            {"name": "Test Shipping Contact", "email": "contact@example.com"}
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.customer.id,
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

    def test_send_mail_action(self):
        self.picking.action_confirm()
        self.picking.action_assign()
        result = self.picking.action_picking_send()
        self.assertEqual(result["name"], "Compose Email")

    def test_send_mail_direct(self):
        self.picking_type.send_delivery_email = True
        self.picking.action_confirm()
        self.picking.action_assign()
        last_known_message = fields.first(self.picking.message_ids)
        self.picking.action_picking_send()
        picking_send_message = self.picking.message_ids[0]
        self.assertNotEqual(last_known_message, picking_send_message)
        self.assertTrue(picking_send_message.attachment_ids)
        template_used = self.picking._get_picking_send_email_template()
        expected_subject = template_used.generate_email(self.picking.id, ["subject"])[
            "subject"
        ]
        self.assertEqual(picking_send_message.subject, expected_subject)
