# Copyright 2024 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
import json
from unittest.mock import patch

from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tests.common import TransactionCase

from odoo.addons.base_exception.exceptions import BaseExceptionError


class TestStockException(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.res_users_model = cls.env["res.users"]
        cls.product_model = cls.env["product.product"]
        cls.exception_rule = cls.env["exception.rule"]

        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.picking_type_id = cls.env.ref("stock.picking_type_out")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

        # Create a product:
        cls.product_1 = cls.product_model.create(
            {
                "name": "Test Product 1",
                "type": "consu",
                "default_code": "PROD1",
                "uom_id": cls.uom_unit.id,
            }
        )

        # Create a Picking:
        cls.picking = cls.env["stock.picking"].create(
            {
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "picking_type_id": cls.picking_type_id.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 1,
                            "uom_id": cls.product_1.uom_id.id,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    )
                ],
            }
        )

    def _store_exceptions(self):
        """Detect without rolling back, so the exceptions are readable here.

        The normal flow stores them in a transaction of its own and rolls this
        one back, so they are not visible from the test.
        """
        self.picking.with_context(
            base_exception_no_rollback={"stock.picking": self.picking.ids}
        ).detect_exceptions()

    def test01_confirm_picking_fail_by_py(self):
        self.stock_exception = self.exception_rule.create(
            {
                "name": "No Partner",
                "sequence": 10,
                "model": "stock.picking",
                "exception_type": "by_py_code",
                "code": "if not self.partner_id: failed=True",
            }
        )
        with self.assertRaises(BaseExceptionError):
            self.picking.action_confirm()
        self._store_exceptions()
        self.assertTrue(self.picking.exceptions_summary)
        self.assertTrue(self.picking.exception_ids)
        rules = self.env["exception.rule"].browse(self.picking.exception_ids.ids)
        self.assertIn(self.picking.id, rules.mapped("picking_ids.id"))

        with self.assertRaises(BaseExceptionError):
            self.picking.button_validate()
        self.assertTrue(self.picking.exceptions_summary)

        # Test ignore exception make possible for the picking to validate
        self.assertEqual(self.picking.state, "draft")
        self.picking.action_ignore_exceptions()
        self.assertTrue(self.picking.ignore_exception)
        self.assertFalse(self.picking.exceptions_summary)
        self.picking.action_confirm()
        self.assertEqual(self.picking.state, "assigned")

    def test02_confirm_picking_fail_by_domain(self):
        self.exception_method = self.env["exception.rule"].create(
            {
                "name": "No Partner",
                "sequence": 11,
                "model": "stock.picking",
                "domain": "[('partner_id', '=', False)]",
                "exception_type": "by_domain",
            }
        )
        with self.assertRaises(BaseExceptionError):
            self.picking.action_confirm()
        self._store_exceptions()
        self.assertTrue(self.picking.exceptions_summary)
        self.assertTrue(self.picking.exception_ids)
        exception_action = self.picking.action_popup_exceptions()
        self.assertEqual(exception_action.get("res_model"), "stock.exception.confirm")
        exception_form = Form(
            self.env["stock.exception.confirm"].with_context(
                **exception_action.get("context")
            ),
        )
        stock_exception = exception_form.save()
        stock_exception.ignore = True
        stock_exception.action_confirm()

    def test03_call_picking_method(self):
        self.env["stock.picking"].test_all_draft_pickings()
        self.env["stock.picking"]._reverse_field()
        self.picking.move_ids._get_main_records()
        self.picking.move_ids._reverse_field()

    def test_confirm_picking(self):
        self.assertEqual(self.picking.state, "draft")
        self.picking.action_confirm()
        self.assertEqual(self.picking.state, "assigned")

    def test04_confirm_moves_of_new_picking(self):
        """A picking confirmed through its moves, in the transaction that
        created it (as a sale order confirmation does), reports the exception
        instead of failing on the uncommitted picking."""
        self.exception_rule.create(
            {
                "name": "No Partner",
                "model": "stock.picking",
                "exception_type": "by_py_code",
                "code": "if not self.partner_id: failed=True",
            }
        )
        picking = self.picking.copy()
        self.assertTrue(picking.move_ids)
        with self.assertRaisesRegex(ValidationError, "No Partner"):
            picking.move_ids._action_confirm()
            self.env.flush_all()

    def test05_cron_stores_exceptions(self):
        self.exception_rule.create(
            {
                "name": "No Partner",
                "model": "stock.picking",
                "exception_type": "by_py_code",
                "code": "if not self.partner_id: failed=True",
            }
        )
        self.env["stock.picking"].test_all_draft_pickings()
        self.assertTrue(self.picking.exception_ids)

    def test06_move_rules_checked_when_picking_rule_applies(self):
        self.exception_rule.create(
            {
                "name": "No Partner",
                "model": "stock.picking",
                "exception_type": "by_py_code",
                "code": "if not self.partner_id: failed=True",
            }
        )
        StockMove = type(self.env["stock.move"])
        with (
            patch.object(
                StockMove, "detect_exceptions", autospec=True, return_value=[]
            ) as detect_move_exceptions,
            self.assertRaises(BaseExceptionError),
        ):
            self.picking.action_confirm()
        detect_move_exceptions.assert_called()

    def test07_move_exception_popups_on_the_picking(self):
        """A move exception opens the popup on the transfer, where it is shown."""
        self.exception_rule.create(
            {
                "name": "Too Many Units",
                "model": "stock.move",
                "exception_type": "by_py_code",
                "code": "if self.product_uom_qty > 0: failed=True",
            }
        )
        with self.assertRaises(BaseExceptionError) as error:
            self.picking.action_confirm()
        self.assertEqual(
            json.loads(error.exception.args[0])["target_model"], "stock.picking"
        )

    def test08_ignore_wizard_returns_confirmation_action(self):
        """Ignoring from the wizard keeps the action the confirmation returns."""
        self.exception_rule.create(
            {
                "name": "No Partner",
                "model": "stock.picking",
                "exception_type": "by_py_code",
                "code": "if not self.partner_id: failed=True",
            }
        )
        self.picking.move_ids.product_uom_qty = 0
        self._store_exceptions()
        wizard = (
            self.env["stock.exception.confirm"]
            .with_context(active_model="stock.picking", active_ids=self.picking.ids)
            .create({"ignore": True})
        )
        with patch("odoo.modules.module.current_test", False):
            action = wizard.action_confirm()
        self.assertEqual(action.get("res_model"), "stock.zero.demand.confirmation")
        self.assertTrue(self.picking.ignore_exception)
