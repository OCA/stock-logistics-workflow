# Copyright 2024 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
import json

from odoo import Command
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.base_exception.exceptions import BaseExceptionError


class TestStockException(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env.ref("product.product_product_4")
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.move_exception = cls.env["exception.rule"].create(
            {
                "name": "Demand Quantity not positive",
                "description": "Demand quantity must be positive",
                "sequence": 50,
                "model": "stock.move",
                "code": "if self.product_uom_qty <= 0: failed = True",
                "active": False,
            }
        )
        cls.picking_exception = cls.env["exception.rule"].create(
            {
                "name": "No Partner",
                "description": "No Partner",
                "sequence": 10,
                "model": "stock.picking",
                "code": "if not self.partner_id: failed = True",
                "active": False,
            }
        )

    def _create_picking(self, product_uom_qty=1):
        return self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": product_uom_qty,
                            "product_uom": self.product.uom_id.id,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                        }
                    )
                ],
            }
        )

    def _assert_blocked(self, method, target_model):
        """Blocked action: catch the error, don't roll the ids back."""
        try:
            method()
        except BaseExceptionError as error:
            values = json.loads(error.args[0])
            self.assertEqual(values["target_model"], target_model)
        else:
            self.fail("BaseExceptionError not raised")

    def test_detect_exceptions(self):
        self.move_exception.active = True
        picking = self._create_picking()
        self.assertFalse(picking.detect_exceptions())
        picking.move_ids.product_uom_qty = 0
        # The exception is found on the move but stored on the picking, so the
        # popup must be displayed on the picking.
        self._assert_blocked(picking.detect_exceptions, "stock.picking")
        picking.invalidate_recordset()
        self.assertIn(self.move_exception, picking.exception_ids)

    def test_detect_exceptions_picking_rule(self):
        self.picking_exception.active = True
        picking = self._create_picking()
        self._assert_blocked(picking.detect_exceptions, "stock.picking")
        picking.invalidate_recordset()
        self.assertIn(self.picking_exception, picking.exception_ids)
        self.assertTrue(picking.main_exception_id)

    def test_onchange_ignore_exception(self):
        picking = self._create_picking()
        picking.action_confirm()
        picking.ignore_exception = True
        picking.onchange_ignore_exception()
        self.assertFalse(picking.ignore_exception)

    def test_action_confirm_with_exceptions(self):
        self.picking_exception.active = True
        # The scheduled action must not fail on pickings with exceptions.
        self.assertTrue(self.env["stock.picking"].test_all_draft_pickings())
        picking = self._create_picking()
        self._assert_blocked(picking.action_confirm, "stock.picking")
        self.assertEqual(picking.state, "draft")
        picking.invalidate_recordset()
        self.assertIn(self.picking_exception, picking.exception_ids)
        action = picking.action_popup_exceptions()
        self.assertEqual(action["res_model"], "stock.exception.confirm")
        with Form(
            self.env["stock.exception.confirm"].with_context(**action["context"])
        ) as form:
            form.ignore = True
        wizard = form.save()
        wizard.action_confirm()
        self.assertNotEqual(picking.state, "draft")

    def test_button_validate_with_exceptions(self):
        picking = self._create_picking()
        picking.action_confirm()
        picking.move_ids.quantity = 1
        picking.move_ids.picked = True
        self.picking_exception.active = True
        self._assert_blocked(picking.button_validate, "stock.picking")
        self.assertIn(self.picking_exception, picking.exception_ids)
        picking.ignore_exception = True
        picking.button_validate()
        self.assertEqual(picking.state, "done")
