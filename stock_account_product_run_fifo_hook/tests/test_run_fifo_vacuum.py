# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.stock_account.tests.test_stockvaluation import (
    _create_accounting_data,
)
from odoo.addons.stock_account.tests.test_stockvaluationlayer import (
    TestStockValuationCommon,
)


class TestRunFifoVacuum(TestStockValuationCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        (
            cls.stock_input_account,
            cls.stock_output_account,
            cls.stock_valuation_account,
            cls.expense_account,
            cls.stock_journal,
        ) = _create_accounting_data(cls.env)
        cls.product1.write({"property_account_expense_id": cls.expense_account.id})
        cls.product1.categ_id.write(
            {
                "property_cost_method": "fifo",
                "property_valuation": "real_time",
                "property_stock_account_input_categ_id": cls.stock_input_account.id,
                "property_stock_account_output_categ_id": (cls.stock_output_account.id),
                "property_stock_valuation_account_id": cls.stock_valuation_account.id,
                "property_stock_journal": cls.stock_journal.id,
            }
        )

    def test_vacuum_uses_the_company_of_the_move(self):
        """The negative stock of company 1 is vacuumed from a receipt validated
        while company 2 is the current company: the valuation of company 1
        (real time) must be used, so every layer gets a journal entry."""
        company1 = self.env.company
        company2 = self.env["res.company"].create({"name": "Other Company"})
        self.env.companies = company1 | company2
        product = self.product1
        product.categ_id.with_company(company2).property_valuation = "manual_periodic"

        self._make_in_move(product, 10, unit_cost=10, create_picking=True)
        self._make_out_move(product, 15, create_picking=True)
        receipt = (
            self.env["stock.picking"]
            .create(
                {
                    "picking_type_id": self.picking_type_in.id,
                    "location_id": self.supplier_location.id,
                    "location_dest_id": self.stock_location.id,
                    "move_ids": [
                        Command.create(
                            {
                                "name": "test fifo",
                                "product_id": product.id,
                                "location_id": self.supplier_location.id,
                                "location_dest_id": self.stock_location.id,
                                "product_uom": self.uom_unit.id,
                                "product_uom_qty": 10,
                                "price_unit": 7,
                            }
                        )
                    ],
                }
            )
            .with_company(company2)
        )
        receipt.action_confirm()
        receipt.button_validate()

        svls = self.env["stock.valuation.layer"].search(
            [("product_id", "=", product.id)]
        )
        self.assertEqual(len(svls), 4)
        self.assertTrue(all(svl.account_move_id for svl in svls))
