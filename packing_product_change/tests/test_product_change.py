# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestProductChange(common.TransactionCase):

    def initial_setup(self):
        self.product = self.env['product.product'].create({
            'name': 'Bread',
            'list_price': 5,
            'type': 'consu', })
        self.replproduct = self.env['product.product'].create({
            'name': 'Meat',
            'list_price': 5,
            'type': 'consu', })
        self.product_uom_unit = self.env.ref('product.product_uom_unit')
        self.partner = self.env['res.partner'].create(
            {'name': 'Imperator Caius Julius Caesar Divus'})
        values = {
            'partner_id': self.partner.id,
            'date_order': '2017-06-15 07:16:27',
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom': self.product_uom_unit.id,
                'price_unit': self.product.list_price,
                'product_uom_qty': 1})], }
        self.sale_ord = self.env['sale.order'].create(values)

    def test_product_change(self):
        self.initial_setup()
        self.sale_ord.action_confirm()
        pickings = self.sale_ord.picking_ids
        move_line = pickings.move_lines
        replwizard = self.env['replace.product'].create(
            {'product_id': self.replproduct.id})
        replwizard.with_context(active_id=move_line.id).replace()
        # check that first product was moved to old product
        # and replacement put in product_id field
        self.assertEqual(move_line.product_id, self.replproduct)
        self.assertEqual(move_line.old_product_id, self.product)
        self.sale_ord.action_invoice_create()
        inv_prod = self.sale_ord.invoice_ids.invoice_line_ids.product_id
        # check that invoice line have replaced product
        self.assertEqual(inv_prod, self.replproduct)
