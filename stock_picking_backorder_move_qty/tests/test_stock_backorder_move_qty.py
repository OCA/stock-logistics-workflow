# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.exceptions import ValidationError
from odoo.tests import Form

from odoo.addons.stock.tests.common import TestStockCommon


class TestStockPickingBackorderMoveQty(TestStockCommon):
    def _prepare_picking(self):
        picking_out_form = Form(self.env["stock.picking"])
        picking_out_form.picking_type_id = self.picking_type_out
        picking_out_form.partner_id = self.partner_1
        for product, qty in [(self.productA, 10), (self.productB, 10)]:
            self.env["stock.quant"]._update_available_quantity(
                product, self.stock_location, 5.0
            )
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
