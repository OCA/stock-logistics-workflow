# Copyright 2019 Komit Consulting - Duc Dao Dong
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests import common


class TestStockLandedCostsCurrency(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestStockLandedCostsCurrency, cls).setUpClass()
        cls.usd_currency = cls.env.ref('base.USD')
        cls.slc_env = cls.env['stock.landed.cost']
        cls.slcl_env = cls.env['stock.landed.cost.lines']
        cls.company = cls.env.ref('base.main_company')
        cls.initial_value = 100
        cls.convert_date = '2019-01-01'

        cls.journal = cls.env['account.journal'].create({
            'name': 'Landed Cost Foreign Journal',
            'type': 'general',
            'code': 'LCF',
            'currency_id': cls.usd_currency.id,
        })
        cls.company_journal = cls.env['account.journal'].create({
            'name': 'Landed Cost Company Journal',
            'type': 'general',
            'code': 'LCC',
            'currency_id': cls.company.currency_id.id,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Shipping Fee',
            'type': 'service',
        })
        cls.product_2 = cls.env['product.product'].create({
            'name': 'Custom Fee',
            'type': 'service',
            'standard_price': 250
        })
        cls.env['res.currency.rate'].create({
            'name': cls.convert_date,
            'currency_id': cls.usd_currency.id,
            'rate': 1.12,
        })
        cls.landed_cost = cls.slc_env.create({
            'date': cls.convert_date,
            'account_journal_id': cls.company_journal.id,
            'currency_id': cls.company_journal.currency_id.id,
            'cost_lines': [(0, 0, {
                'product_id': cls.product.id,
                'split_method': 'equal',
                'currency_price_unit': cls.initial_value,
                'price_unit': cls.initial_value  # Same currency as company
            })]
        })

    def test_foreign_currency_landed_cost(cls):
        # Create Landed Cost
        landed_cost = cls.slc_env.new({
            'date': cls.convert_date,
            'account_journal_id': cls.journal.id,
        })
        landed_cost._onchange_account_journal_id()
        landed_cost = cls.slc_env.create(
            landed_cost._convert_to_write(landed_cost._cache))

        # Create Landed Cost Line
        cost_line = cls.slcl_env.new({
            'cost_id': landed_cost.id,
            'product_id': cls.product.id,
            'split_method': 'equal',
            'currency_price_unit': cls.initial_value
        })
        landed_cost._onchange_currency_id()
        cost_line._onchange_currency_price_unit()

        cost_line = cls.slcl_env.create(
            cost_line._convert_to_write(cost_line._cache))

        expected_value = cls.journal.currency_id._convert(
            cls.initial_value, cls.company.currency_id,
            cls.company, cls.convert_date)

        cls.assertEqual(cost_line.price_unit, expected_value)

    def test_change_journal_landed_cost(cls):
        cls.landed_cost.write({'account_journal_id': cls.journal.id})
        cls.landed_cost._onchange_account_journal_id()
        cls.landed_cost._onchange_currency_id()

        cost_line = cls.landed_cost.cost_lines[0]
        expected_value = cls.journal.currency_id._convert(
            cls.initial_value, cls.company.currency_id,
            cls.company, cls.convert_date)

        cls.assertEqual(cost_line.price_unit, expected_value)

    def test_change_currency_landed_cost(cls):
        cls.landed_cost.write({'currency_id': cls.usd_currency.id})
        cls.landed_cost._onchange_currency_id()

        cost_line = cls.landed_cost.cost_lines[0]
        expected_value = cls.usd_currency._convert(
            cls.initial_value, cls.company.currency_id,
            cls.company, cls.convert_date)

        cls.assertEqual(cost_line.price_unit, expected_value)

    def test_change_product_landed_cost(cls):
        cost_line = cls.landed_cost.cost_lines[0]
        cost_line.write({'product_id': cls.product_2.id})
        cost_line.onchange_product_id()

        expected_value = cls.product_2.standard_price

        cls.assertEqual(cost_line.currency_price_unit, expected_value)
