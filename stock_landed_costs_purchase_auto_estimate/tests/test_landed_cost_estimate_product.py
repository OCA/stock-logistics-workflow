# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestPurchaseStockLandedCostEstimateBase


class TestLandedCostEstimateProduct(TestPurchaseStockLandedCostEstimateBase):
    """Estimates posted against the configured estimated-landed-cost product."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Account = cls.env["account.account"]
        cls.valuation_account = Account.create(
            {
                "name": "Stock on hand (test)",
                "code": "TESTLC.STOCK",
                "account_type": "asset_current",
                "company_ids": [(4, cls.company.id)],
            }
        )
        cls.freight_account = Account.create(
            {
                "name": "Incoming freight (test)",
                "code": "TESTLC.FREIGHT",
                "account_type": "expense_direct_cost",
                "company_ids": [(4, cls.company.id)],
            }
        )
        category = cls.category.with_company(cls.company)
        category.property_valuation = "real_time"
        category.property_stock_valuation_account_id = cls.valuation_account
        # the landed-cost entry only posts for valued (storable) receipts
        cls.product_storable.is_storable = True
        cls.lc_product = cls.env["product.product"].create(
            {
                "name": "Estimated freight-in (test)",
                "type": "service",
                "landed_cost_ok": True,
                "split_method_landed_cost": "by_current_cost_price",
            }
        )
        cls.lc_product.product_tmpl_id.with_company(
            cls.company
        ).property_account_expense_id = cls.freight_account
        cls.company.estimated_landed_cost_product_id = cls.lc_product

    def test_estimate_uses_configured_product(self):
        """One cost line on the configured product, with no explicit account."""
        self.order.button_confirm()
        line = self.order.landed_cost_ids.cost_lines
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_id, self.lc_product)
        # 10% of the 10.00 order line
        self.assertAlmostEqual(line.price_unit, 1.0)
        self.assertEqual(line.split_method, "by_current_cost_price")
        self.assertFalse(line.account_id)

    def test_entry_debits_stock_credits_freight(self):
        """The validated estimate posts Dr stock valuation / Cr freight."""
        self.order.button_confirm()
        self._action_picking_validate(self.order.picking_ids)
        landed_cost = self.order.landed_cost_ids
        self.assertEqual(landed_cost.state, "done")
        move = landed_cost.account_move_id
        self.assertTrue(move)
        debit = move.line_ids.filtered("debit")
        credit = move.line_ids.filtered("credit")
        self.assertEqual(debit.account_id, self.valuation_account)
        self.assertAlmostEqual(debit.debit, 1.0)
        self.assertEqual(credit.account_id, self.freight_account)
        self.assertAlmostEqual(credit.credit, 1.0)
        # the receipt carries the uplifted value (10.00 + 1.00)
        self.assertAlmostEqual(self.order.picking_ids.move_ids.value, 11.0)

    def test_without_setting_keeps_default_behaviour(self):
        """No configured product: the purchased product stays on the line."""
        self.company.estimated_landed_cost_product_id = False
        self.order.button_confirm()
        line = self.order.landed_cost_ids.cost_lines
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_id, self.order.order_line.product_id)
        self.assertEqual(line.account_id, self.valuation_account)

    def test_multi_line_order_sums_into_single_line(self):
        """Several order lines produce one summed estimate line."""
        other = self.env["product.product"].create(
            {
                "name": "Producto Storable 2",
                "type": "consu",
                "is_storable": True,
                "categ_id": self.category.id,
            }
        )
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.partner.id,
                "product_id": other.id,
                "price": 20,
                "indirect_cost_percent": 10,
            }
        )
        self.env["purchase.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": other.id,
                "product_qty": 1,
                "price_unit": 20,
            }
        )
        self.order.button_confirm()
        line = self.order.landed_cost_ids.cost_lines
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_id, self.lc_product)
        # 10% of 10.00 + 10% of 20.00
        self.assertAlmostEqual(line.price_unit, 3.0)
