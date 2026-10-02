# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import Command
from odoo.tests import TransactionCase, tagged

from odoo.addons.queue_job.tests.common import trap_jobs


@tagged("post_install", "-at_install")
class TestStockPickingConfirmationEmailQueueJob(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.stock_move_email_validation = True
        cls.template = cls.env.company.stock_mail_confirmation_template_id
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test customer", "email": "customer@example.com"}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "is_storable": True}
        )
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.warehouse.lot_stock_id, 10
        )

    @classmethod
    def _create_picking(cls, picking_type):
        picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "partner_id": cls.partner.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "location_id": picking_type.default_location_src_id.id,
                            "location_dest_id": (
                                picking_type.default_location_dest_id.id
                            ),
                        }
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.quantity = 1
        picking.move_ids.picked = True
        return picking

    def _confirmation_messages(self, picking):
        return picking.message_ids.filtered(
            lambda m: m.subject
            and "Delivery Order" in m.subject
            and picking.name in m.subject
        )

    def test_delivery_confirmation_email_delayed(self):
        picking = self._create_picking(self.warehouse.out_type_id)
        with trap_jobs() as trap:
            picking.button_validate()
            self.assertEqual(picking.state, "done")
            trap.assert_jobs_count(1, only=picking._post_confirmation_email)
            self.assertFalse(self._confirmation_messages(picking))
            trap.perform_enqueued_jobs()
        message = self._confirmation_messages(picking)
        self.assertEqual(len(message), 1)
        self.assertIn(self.partner, message.partner_ids)
        self.assertTrue(message.attachment_ids)

    def test_delivery_confirmation_email_no_delay(self):
        picking = self._create_picking(self.warehouse.out_type_id)
        with trap_jobs() as trap:
            picking.with_context(queue_job__no_delay=True).button_validate()
            trap.assert_jobs_count(0)
        self.assertEqual(len(self._confirmation_messages(picking)), 1)
