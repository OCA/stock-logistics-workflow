# Copyright 2026 Ecosoft (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStockFiscalPosition(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fiscal_position_obj = cls.env["account.fiscal.position"]
        cls.account_obj = cls.env["account.account"]
        cls.valuation_account = cls.account_obj.create(
            {
                "name": "Test stock valuation",
                "code": "tv",
                "account_type": "liability_current",
                "reconcile": True,
                "company_ids": [Command.link(cls.env.ref("base.main_company").id)],
            }
        )
        cls.stock_input_account = cls.account_obj.create(
            {
                "name": "Test stock input",
                "code": "tsti",
                "account_type": "expense",
                "reconcile": True,
                "company_ids": [Command.link(cls.env.ref("base.main_company").id)],
            }
        )
        cls.stock_output_account = cls.account_obj.create(
            {
                "name": "Test stock output",
                "code": "tout",
                "account_type": "income",
                "reconcile": True,
                "company_ids": [Command.link(cls.env.ref("base.main_company").id)],
            }
        )
        cls.stock_journal = cls.env["account.journal"].create(
            {"name": "Stock Journal", "code": "STJTEST", "type": "general"}
        )

        cls.expense_account = cls.account_obj.create(
            {
                "name": "Test Expense1",
                "code": "extst",
                "account_type": "expense",
                "reconcile": True,
                "company_ids": [Command.link(cls.env.ref("base.main_company").id)],
            }
        )
        cls.revenue_account = cls.account_obj.create(
            {
                "name": "Test Revenue1",
                "code": "inct1",
                "account_type": "income",
                "reconcile": True,
                "company_ids": [Command.link(cls.env.ref("base.main_company").id)],
            }
        )

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.location = cls.warehouse.lot_stock_id
        cls.dest_location = cls.env.ref("stock.stock_location_customers")
        cls.outgoing_picking_type = cls.env.ref("stock.picking_type_out")
        cls.incoming_picking_type = cls.env.ref("stock.picking_type_in")

        cls.product_categ = cls.env.ref("product.product_category_5")
        cls.product_categ.update(
            {
                "property_valuation": "real_time",
                "property_stock_valuation_account_id": cls.valuation_account.id,
                "property_stock_account_input_categ_id": cls.stock_input_account.id,
                "property_stock_account_output_categ_id": cls.stock_output_account.id,
                "property_stock_journal": cls.stock_journal.id,
            }
        )

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
                "standard_price": 1.0,
                "categ_id": cls.product_categ.id,
            }
        )

        # Fiscal Position: map Stock Input -> Expense, Stock Output -> Revenue
        cls.fiscal_position = cls.fiscal_position_obj.create(
            {
                "name": "Test FP: Remap Stock Accounts",
                "account_ids": [
                    Command.create(
                        {
                            "account_src_id": cls.stock_input_account.id,
                            "account_dest_id": cls.expense_account.id,
                        }
                    ),
                    Command.create(
                        {
                            "account_src_id": cls.stock_output_account.id,
                            "account_dest_id": cls.revenue_account.id,
                        }
                    ),
                ],
            }
        )

        # Picking type without FP
        cls.picking_type_no_fp = cls.warehouse.in_type_id.copy(
            {"name": "Receipts (No FP)"}
        )

        # Picking type with FP
        cls.picking_type_with_fp = cls.warehouse.in_type_id.copy(
            {
                "name": "Receipts (With FP)",
                "fiscal_position_id": cls.fiscal_position.id,
            }
        )

    def _create_receipt(self, picking_type):
        """Create, confirm, and validate a receipt picking."""
        receipt = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "test receipt move",
                            "product_id": self.product1.id,
                            "product_uom_qty": 10,
                        }
                    )
                ],
            }
        )
        receipt.button_validate()
        return receipt

    def _get_je_accounts(self, picking):
        """Return all accounts used in JEs generated by a picking's moves."""
        account_moves = picking.move_ids.account_move_ids
        return account_moves.line_ids.mapped("account_id")

    def test_01_no_fiscal_position(self):
        """Picking type has no FP configured.

        Flow:
        - Create picking -> picking.fiscal_position_id is empty
        - Validate -> JE uses standard stock accounts (no mapping applied)
        """
        receipt = self._create_receipt(self.picking_type_no_fp)

        # Picking must have no fiscal position
        self.assertFalse(
            receipt.fiscal_position_id,
            "Picking should have no fiscal_position_id when picking type has none",
        )

        # JE must use normal stock_input_account (not remapped to expense)
        je_accounts = self._get_je_accounts(receipt)
        self.assertTrue(je_accounts, "JE should be created (real-time valuation)")
        self.assertIn(
            self.stock_input_account,
            je_accounts,
            "JE credit line should use stock input account (no FP mapping)",
        )
        self.assertNotIn(
            self.expense_account,
            je_accounts,
            "JE should NOT use expense account when no FP",
        )

    def test_02_with_fiscal_position(self):
        """Picking type has FP configured (maps stock_input -> expense).

        Flow:
        - Create picking -> picking.fiscal_position_id = fiscal_position
        - Validate -> JE account is remapped by FP
        """
        receipt = self._create_receipt(self.picking_type_with_fp)

        # Picking must inherit FP from picking type
        self.assertEqual(
            receipt.fiscal_position_id,
            self.fiscal_position,
            "Picking should inherit fiscal_position_id from picking type",
        )

        # JE must use mapped account (expense_account), not original stock_input_account
        je_accounts = self._get_je_accounts(receipt)
        self.assertTrue(je_accounts, "JE should be created (real-time valuation)")
        self.assertIn(
            self.expense_account,
            je_accounts,
            "JE credit line should be remapped to expense account by FP",
        )
        self.assertNotIn(
            self.stock_input_account,
            je_accounts,
            "JE should NOT use original stock input account when FP remaps it",
        )
