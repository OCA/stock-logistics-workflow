# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from odoo.tests import common
from odoo import fields
from odoo.osv import expression
from odoo.exceptions import ValidationError


class TestChangePriceAtDate(common.TransactionCase):

    def setUp(self):
        super(TestChangePriceAtDate, self).setUp()
        self.wizard_obj = self.env['stock.change.standard.price']
        self.move_line_obj = self.env['account.move.line']
        self.product = self.env.ref('stock.product_icecream')
        self.product.categ_id.property_stock_journal = self.env[
            'account.journal'].create({
                'name': 'Stock journal',
                'type': 'sale',
                'code': 'STK00'})
        # Defining accounts
        self.account = self.env['account.account'].create({
            'name': 'TEST ACCOUNT',
            'code': 'TEST',
            'user_type_id': self.env.ref(
                'account.data_account_type_expenses').id,
        })

        self.loc_account = self.env['account.account'].create({
            'name': 'STOCK LOC ACCOUNT',
            'code': 'STOCK',
            'user_type_id': self.env.ref(
                'account.data_account_type_expenses').id,
        })
        self.inventory_account = self.env['account.account'].create({
            'name': 'Inventory ACCOUNT',
            'code': 'INV',
            'user_type_id': self.env.ref(
                'account.data_account_type_expenses').id,
        })
        self.product.categ_id.property_account_income_categ_id = self.account
        self.product.categ_id.property_stock_valuation_account_id = \
            self.loc_account
        self.product.property_stock_inventory.valuation_out_account_id = \
            self.inventory_account
        self.product.valuation = 'real_time'
        self.location = self.browse_ref('stock.warehouse0').lot_stock_id
        self.location.valuation_out_account_id = self.loc_account
        self.location.valuation_in_account_id = self.loc_account

    def _set_inventory(self, product, date_time=None):
        vals = {
            'name': 'Test stock available for reservation',
            'location_id': self.location.id,
            'filter': 'none'
        }
        inventory_obj = self.env['stock.inventory']
        # Set context to simulate the date
        if date_time:
            vals.update({
                'date': date_time,
            })
            inventory_obj = self.env['stock.inventory'].with_context(
                date=date_time,
                force_period_date=fields.Date.to_string(date_time)
            )
        inventory = inventory_obj.create(vals)
        inventory.prepare_inventory()
        self.env['stock.inventory.line'].create({
            'inventory_id': inventory.id,
            'product_id': product.id,
            'location_id': self.location.id,
            'product_qty': 10.0})
        inventory.action_done()

    def _change_price(self, new_price, move_date=None, template=False):
        """
        Launch wizard to change price
        Set date in context for moves if filled in
        :param new_price: New Price
        :param move_date: The date of the account move
        """
        if template:
            active_id = self.product.product_tmpl_id.id
            active_model = 'product.template'
        else:
            active_id = self.product.id
            active_model = 'product.product'
        wizard_context = self.wizard_obj.with_context(
            active_id=active_id,
            active_model=active_model)
        if move_date:
            wizard_context = self.wizard_obj.with_context(
                active_id=active_id,
                active_model=active_model,
                date=move_date,
                force_period_date=fields.Date.to_string(move_date),
            )
        self.wizard = wizard_context.create({
            'counterpart_account_id': self.account.id,
            'new_price': new_price,
            'date': move_date or False})
        self.wizard.change_price()

    def _get_move_line_domain(self, template=False):
        product_domain = [('product_id', '=', self.product.id)]
        if template:
            product_domain = [
                ('product_id',
                 'in',
                 self.product.product_tmpl_id.product_variant_ids.ids)
            ]
        return expression.AND([
            product_domain,
            [('move_id.state', '=', 'posted')],
        ])

    def _create_variant(self):
        vals = {
            'name': 'Strawberry',
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'standard_price': 75.0,
        }
        return self.env['product.product'].create(vals)

    def test_change_price(self):
        # Change Price to 80.0 (standard one)
        # Change Price to 60.0 3 days ago
        # Check if product standard price is 80.0
        # Check if move line is created

        self._set_inventory(self.product)
        # Product price before tests was 70.0

        self._change_price(80.0)
        move_lines = self.move_line_obj.search(
            self._get_move_line_domain(),
        )
        self.assertEquals(
            80.0,
            self.product.standard_price,
        )
        move_date = fields.Date.from_string(
            fields.Date.today()) - timedelta(days=3)

        self._change_price(60.0, move_date)

        new_lines = self.move_line_obj.search(
            self._get_move_line_domain()
        ) - move_lines

        self.assertEquals(
            80.0,
            self.product.standard_price,
        )
        self.assertEquals(
            2,
            len(new_lines)
        )

    def test_change_template_price(self):
        # Create a variant on template
        # Change Price to 80.0 (standard one) for template
        # Change Price to 60.0 3 days ago for template
        # Check if product variants standard price is 80.0
        # Check if move lines are created
        # Set inventory on product 2

        self._set_inventory(self.product)
        # Product price before tests was 70.0

        product_2 = self._create_variant()
        self._change_price(80.0, template=True)
        move_lines = self.move_line_obj.search(
            self._get_move_line_domain(template=True),
        )
        self.assertEquals(
            80.0,
            self.product.standard_price,
        )
        self.assertEquals(
            80.0,
            product_2.standard_price,
        )
        move_date = fields.Date.from_string(
            fields.Date.today()) - timedelta(days=3)

        self._change_price(60.0, move_date, template=True)

        new_lines = self.move_line_obj.search(
            self._get_move_line_domain(template=True)
        ) - move_lines

        self.assertEquals(
            80.0,
            self.product.standard_price,
        )
        self.assertEquals(
            60.0,
            product_2.standard_price,
        )
        self.assertEquals(
            2,
            len(new_lines)
        )
        # Only product 1 has inventory, so move lines are generated for that
        # one only
        self.assertEquals(
            self.product,
            new_lines.mapped('product_id'),
        )
        # Set Inventory on product 2
        self._set_inventory(product_2)
        move_lines = self.move_line_obj.search(
            self._get_move_line_domain(template=True),
        )
        self._change_price(50.0, move_date, template=True)

        new_lines = self.move_line_obj.search(
            self._get_move_line_domain(template=True)
        ) - move_lines
        self.assertEquals(
            4,
            len(new_lines)
        )
        # Product 2 standard price hasn't changed
        self.assertEquals(
            60.0,
            product_2.standard_price,
        )

    def test_change_one_product_in_template_price(self):
        # Create a variant on template
        # Set inventory on that product 3 days ago
        # Change Price to 80.0 3 days ago for template
        # Check if product variants standard price is 80.0

        self._set_inventory(self.product)
        # Product price before tests was 70.0

        product_2 = self._create_variant()
        now_value = fields.Datetime.from_string(
            fields.Datetime.now()) - timedelta(days=3)
        self._set_inventory(
            product_2, date_time=now_value)

        # Change prices
        move_date = fields.Date.from_string(
            fields.Date.today()) - timedelta(days=2)
        self._change_price(80.0, move_date=move_date, template=True)

        # Just product 2 standard price should have been changed
        self.assertEquals(
            80.0,
            product_2.standard_price,
        )
        self.assertEquals(
            70.0,
            self.product.standard_price,
        )

    def test_change_future_price(self):
        # Try to change price to future date
        move_date = fields.Date.from_string(
            fields.Date.today()) + timedelta(days=3)
        with self.assertRaises(ValidationError):
            self._change_price(60.0, move_date, template=True)
