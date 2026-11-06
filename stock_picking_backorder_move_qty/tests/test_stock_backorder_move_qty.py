# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.exceptions import ValidationError
from odoo.tests import Form

from odoo.addons.stock.tests.common import TestStockCommon


class TestStockPickingBackorderMoveQty(TestStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_product_qty_tuples = [(cls.productA, 5), (cls.productB, 5)]
        cls._init_stock_inventory()

    @classmethod
    def _init_stock_inventory(cls, product_qty_tuples=None):
        if product_qty_tuples is None:
            product_qty_tuples = cls.default_product_qty_tuples
        for product, qty in product_qty_tuples:
            cls.env["stock.quant"]._update_available_quantity(
                product, cls.stock_location, qty
            )

    def _prepare_picking(self):
        picking_out_form = Form(self.env["stock.picking"])
        picking_out_form.picking_type_id = self.picking_type_out
        picking_out_form.partner_id = self.partner_1
        for product, qty in [(self.productA, 10), (self.productB, 10)]:
            with picking_out_form.move_ids.new() as move:
                move.product_id = product
                move.product_uom_qty = qty
        return picking_out_form.save()

    def test_backorder_no_qty(self):
        """Ensure no backorders are generated in case we do not have any quantity"""
        picking_out = self._prepare_picking()
        picking_out.action_confirm()
        picking_out.action_assign()
        backorder_action = picking_out.button_validate()
        wizard_form = Form(
            self.env[backorder_action["res_model"]]
            .with_context(**backorder_action["context"])
            .create({})
        )
        # ProductA
        with wizard_form.backorder_confirmation_move_line_ids.edit(0) as wiz_line_form:
            wiz_line_form.qty_to_backorder = 0
        # ProductB
        wizard_form.backorder_confirmation_move_line_ids.remove(index=1)
        wizard = wizard_form.save()
        wizard.process()
        self.assertEqual(picking_out.state, "done")
        self.assertFalse(picking_out.backorder_ids)

    def test_backorder_partial_move_qty(self):
        """Ensure only partial quantity provided in wizard are backordered"""
        picking_out = self._prepare_picking()
        picking_out.action_confirm()
        picking_out.action_assign()
        backorder_action = picking_out.button_validate()
        wizard_form = Form(
            self.env[backorder_action["res_model"]]
            .with_context(**backorder_action["context"])
            .create({})
        )
        product_backorder_qties = {
            self.productA.id: 2,
            self.productB.id: 3,
        }
        for idx, _ in enumerate(
            wizard_form.backorder_confirmation_move_line_ids._records
        ):
            with wizard_form.backorder_confirmation_move_line_ids.edit(
                idx
            ) as wiz_line_form:
                wiz_line_form.qty_to_backorder = product_backorder_qties[
                    wiz_line_form.move_id.product_id.id
                ]
        wizard = wizard_form.save()
        wizard.process()
        backorder = picking_out.backorder_ids
        self.assertTrue(backorder.move_ids)
        for move in backorder.move_ids:
            self.assertEqual(
                move.product_uom_qty, product_backorder_qties[move.product_id.id]
            )

    def test_wizard_constrains_no_negative(self):
        """Ensure negative quantity is not allowed in wizard"""
        picking_out = self._prepare_picking()
        picking_out.action_confirm()
        picking_out.action_assign()
        backorder_action = picking_out.button_validate()
        wizard = (
            self.env[backorder_action["res_model"]]
            .with_context(**backorder_action["context"])
            .create({})
        )
        with self.assertRaisesRegex(ValidationError, "cannot be negative"):
            wizard.backorder_confirmation_move_line_ids[:1].qty_to_backorder = -1

    def test_wizard_backorder_only_remaining_lines(self):
        self._init_stock_inventory([(self.productA, 20), (self.productB, 20)])
        picking_out = self._prepare_picking()
        picking_out.action_confirm()
        picking_out.action_assign()

        first_move = picking_out.move_ids.filtered(
            lambda mov: mov.product_id == self.productA
        )
        first_move.quantity = 0

        backorder_action = picking_out.button_validate()
        wizard = (
            self.env[backorder_action["res_model"]]
            .with_context(**backorder_action["context"])
            .create({})
        )
        wizard_line = wizard.backorder_confirmation_move_line_ids
        self.assertEqual(len(wizard_line), 1)
        self.assertEqual(wizard_line.move_id, first_move)

    def test_wizard_constrains_no_exceed_remaining(self):
        """Ensure more quantity is not allowed in wizard"""
        picking_out = self._prepare_picking()
        picking_out.action_confirm()
        picking_out.action_assign()
        backorder_action = picking_out.button_validate()
        wizard = (
            self.env[backorder_action["res_model"]]
            .with_context(**backorder_action["context"])
            .create({})
        )
        with self.assertRaisesRegex(
            ValidationError, "cannot exceed the remaining unprocessed quantity"
        ):
            wizard.backorder_confirmation_move_line_ids[:1].qty_to_backorder = (
                wizard.backorder_confirmation_move_line_ids[:1].qty_unprocessed + 1
            )

    def test_wizard_allow_bigger_qty(self):
        self._init_stock_inventory([(self.productA, 20), (self.productB, 20)])
        picking_out = self._prepare_picking()
        picking_out.action_confirm()
        picking_out.action_assign()

        first_move = picking_out.move_ids.filtered(
            lambda mov: mov.product_id == self.productA
        )
        second_move = picking_out.move_ids.filtered(
            lambda mov: mov.product_id == self.productB
        )

        self.assertEqual(first_move.quantity, 10)
        self.assertEqual(second_move.quantity, 10)
        # Increase quantity on first move
        first_move.quantity = 15.0
        # Set only other move as picked
        second_move.picked = True

        backorder_action = picking_out.button_validate()
        wizard = (
            self.env[backorder_action["res_model"]]
            .with_context(**backorder_action["context"])
            .create({})
        )
        wizard_line = wizard.backorder_confirmation_move_line_ids
        self.assertEqual(len(wizard_line), 1)
        self.assertEqual(wizard_line.move_id, first_move)
        self.assertEqual(wizard_line.qty_to_backorder, 15.0)

        wizard.process()
        backorder = picking_out.backorder_ids
        backorder_move = backorder.move_ids
        self.assertEqual(backorder_move.product_uom_qty, 10.0)
        self.assertEqual(backorder_move.quantity, 15.0)
