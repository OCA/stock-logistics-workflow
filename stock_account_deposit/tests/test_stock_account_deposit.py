# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common


class TestStockAccountDeposit(common.TransactionCase):

    def setUp(self):
        super(TestStockAccountDeposit, self).setUp()
        self.Location = self.env['stock.location']
        self.PickingType = self.env['stock.picking.type']
        self.Picking = self.env['stock.picking']
        self.Product = self.env['product.template']
        self.warehouse = self.env['stock.warehouse'].create({
            'name': 'warehouse - test',
            'code': 'WH-TEST',
        })
        self.deposit_location = self.Location.search([
            ('deposit_location', '=', True),
            ('location_id', '=', self.warehouse.lot_stock_id.id),
        ])
        self.product = self.Product.create({
            'name': 'Product - Deposit - Test',
            'type': 'product',
            'list_price': 100.00,
            'standard_price': 100.00,
        })
        self.qty_on_hand()
        self.customer = self.env['res.partner'].create({
            'name': 'Customer - test',
            'customer': True,
        })

    def qty_on_hand(self):
        stock_change_obj = self.env['stock.change.product.qty']
        vals = {
            'product_id': self.product.product_variant_ids[:1].id,
            'new_quantity': 200.0,
            'location_id': self.warehouse.lot_stock_id.id,
        }
        wiz = stock_change_obj.create(vals)
        wiz.change_product_qty()

    def _prepare_picking(self):
        picking_type = self.PickingType.search([
            ('warehouse_id', '=', self.warehouse.id),
            ('default_location_src_id', '=', self.warehouse.lot_stock_id.id),
            ('is_deposit', '=', True),
        ])
        picking = self.Picking.create({
            'name': 'picking - test 01',
            'location_id': self.warehouse.lot_stock_id.id,
            'location_dest_id': self.deposit_location.id,
            'owner_id': self.customer.id,
            'picking_type_id': picking_type.id,
            'move_lines': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.product_variant_ids[:1].id,
                'product_uom_qty': 20.0,
                'product_uom': self.product.uom_id.id,
            })]
        })
        return picking

    def test_deposit_regularize_invoice(self):
        picking = self._prepare_picking()
        picking.action_assign()
        picking.do_transfer()

        stock_moves = self.env['stock.move'].search([
            ('picking_id', '=', picking.id)
        ])
        quants_to_regularize = stock_moves.quant_ids.filtered(
            lambda x: x.location_id.deposit_location)
        regularize_obj = self.env['deposit.stock.quant.wizard']
        vals = {
            'quants_action': 'invoice',
        }
        regularize = regularize_obj.with_context(
            active_ids=quants_to_regularize.ids,
            warehouse=self.warehouse.id
        ).create(vals)
        invoice_view = regularize.action_apply()
        self.assertTrue(invoice_view)
        Invoice = self.env['account.invoice']
        invoice = Invoice.search(invoice_view['domain'])
        product = invoice.invoice_line_ids[:1].product_id
        product_qty = invoice.invoice_line_ids[:1].quantity
        self.assertEquals(len(invoice.invoice_line_ids), 1)
        self.assertEquals(product_qty, 20)
        self.assertEquals(product, self.product.product_variant_ids[:1])
