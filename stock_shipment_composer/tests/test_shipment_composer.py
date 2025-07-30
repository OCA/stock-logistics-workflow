# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from datetime import timedelta

from odoo import Command, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestShipmentComposer(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.picking_type_out = cls.wh.out_type_id
        cls.stock_loc = cls.wh.lot_stock_id
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {"name": "test", "type": "product"}
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.stock_loc, 5.0
        )
        cls.picking = cls.create_picking(cls.partner)
        cls.picking.action_confirm()
        cls.move = cls.picking.move_ids
        # Adjust scheduled_date to test compute
        cls.picking.scheduled_date = fields.Datetime.now() + timedelta(days=1)
        cls.composer1 = cls.create_composer()
        cls.line1 = cls.create_composer_line(cls.composer1, cls.move, quantity=5.0)

    @classmethod
    def create_picking(cls, partner):
        picking = cls.env["stock.picking"].create(
            {
                "location_id": cls.stock_loc.id,
                "location_dest_id": cls.customer_loc.id,
                "partner_id": partner.id,
                "picking_type_id": cls.picking_type_out.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "Test",
                            "partner_id": partner.id,
                            "location_id": cls.stock_loc.id,
                            "location_dest_id": cls.customer_loc.id,
                            "product_id": cls.product.id,
                            "product_uom_qty": 5.0,
                        }
                    )
                ],
            }
        )
        return picking

    @classmethod
    def create_composer(cls, partner=None, picking_type=None):
        partner = partner or cls.partner
        picking_type = picking_type or cls.picking_type_out
        return cls.env["stock.shipment.composer"].create(
            {"partner_id": partner.id, "picking_type_id": picking_type.id}
        )

    @classmethod
    def create_composer_line(cls, composer, move, quantity=1.0):
        return cls.env["stock.shipment.composer.line"].create(
            {
                "composer_id": composer.id,
                "move_id": move.id,
                "quantity": quantity,
            }
        )

    def test_compute_scheduled_date(self):
        self.composer1._compute_scheduled_date()
        self.assertEqual(self.composer1.scheduled_date, self.picking.scheduled_date)

    def test_action_confirm_and_assign(self):
        self.assertEqual(self.composer1.state, "draft")
        self.composer1.action_confirm()
        self.assertEqual(self.composer1.state, "in_progress")
        self.picking.do_unreserve()
        self.assertEqual(self.picking.state, "confirmed")
        self.composer1.action_assign()
        self.assertEqual(self.picking.state, "assigned")

    def test_action_done_success_flow(self):
        self.composer1.action_confirm()
        res = self.composer1.action_done()
        self.assertEqual(res, True)
        self.assertEqual(self.picking.state, "done")
        self.assertEqual(self.composer1.state, "done")
        self.assertTrue(self.composer1.date_done)
        self.assertEqual(self.move.quantity_done, 5.0)
        self.assertEqual(self.move.shipment_composer_id, self.composer1)

    def test_action_done_success_flow_with_backorder(self):
        self.line1.quantity = 3.0
        self.composer2 = self.create_composer()
        self.line2 = self.create_composer_line(self.composer2, self.move, quantity=2.0)
        self.composer1.action_confirm()
        # There should be a wizard asking to process picking without quantity done
        backorder_wizard_dict = self.composer1.action_done()
        self.assertTrue(backorder_wizard_dict)
        backorder_wizard = Form(
            self.env[(backorder_wizard_dict.get("res_model"))].with_context(
                **backorder_wizard_dict["context"]
            )
        ).save()
        self.assertEqual(len(backorder_wizard.pick_ids), 1)
        backorder_wizard.process()
        self.assertEqual(self.picking.state, "done")
        self.assertEqual(self.composer1.state, "done")
        self.assertTrue(self.composer1.date_done)
        self.assertEqual(self.move.quantity_done, 3.0)
        new_move = self.picking.backorder_ids.move_ids
        self.assertEqual(self.line2.move_id, new_move)

    def test_action_done_quantity_zero_error(self):
        # set one line to zero and expect error
        self.line1.quantity = 0.0
        self.composer1.action_confirm()
        with self.assertRaises(UserError):
            self.composer1.action_done()

    def test_action_done_reserved_short_error(self):
        # Reduce availability to 2 (less than the move qty 3)
        # Remove 1 reserved by decreasing available stock and unassign/assign again
        self.picking.do_unreserve()
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_loc, -3.0
        )
        self.picking.action_assign()
        self.composer1.action_confirm()
        with self.assertRaises(UserError):
            self.composer1.action_done()

    def test_picking_button_validate_blocked_by_active_composer(self):
        self.composer1.action_confirm()
        with self.assertRaises(UserError):
            self.picking.button_validate()
        self.composer1.action_cancel()
        self.picking.button_validate()

    def test_quantity_constraint_against_move_qty(self):
        self.line1.quantity = 6.0
        with self.assertRaises(ValidationError):
            self.composer1.action_confirm()
        self.line1.quantity = 4.0
        self.composer2 = self.create_composer()
        self.line2 = self.create_composer_line(self.composer2, self.move, quantity=2.0)
        self.composer1.action_confirm()
        with self.assertRaises(ValidationError):
            self.composer2.action_confirm()
        self.line2.quantity = 1.0
        self.composer2.action_confirm()
        with self.assertRaises(ValidationError):
            self.line2.quantity = 2.0

    def test_create_composer_from_stock_move(self):
        move1 = self.create_picking(self.partner).move_ids
        move2 = self.create_picking(self.partner).move_ids
        test_partner = self.env["res.partner"].create({"name": "Test"})
        move3 = self.create_picking(test_partner).move_ids
        with self.assertRaises(UserError):
            self.env["stock.shipment.composer.wizard"].with_context(
                active_ids=[move1.id, move2.id, move3.id]
            ).create({})
        wizard = (
            self.env["stock.shipment.composer.wizard"]
            .with_context(active_ids=[move1.id, move2.id])
            .create({})
        )
        self.assertEqual(wizard.partner_id, self.partner)
        self.assertEqual(len(wizard.line_ids), 2)
        wizard.line_ids[0].quantity = 1.0
        wizard.line_ids[1].quantity = 1.0
        composer_action = wizard.action_create_composer()
        composer = self.env["stock.shipment.composer"].browse(composer_action["res_id"])
        self.assertEqual(composer.partner_id, self.partner)
        self.assertEqual(composer.picking_type_id, self.picking_type_out)
        self.assertEqual(len(composer.line_ids), 2)
        self.assertEqual(set(composer.line_ids.mapped("move_id")), {move1, move2})
        self.assertEqual(composer.line_ids[0].quantity, 1.0)
        self.assertEqual(composer.line_ids[1].quantity, 1.0)
