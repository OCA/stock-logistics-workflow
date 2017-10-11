# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common
from openerp.exceptions import ValidationError


class TestStockDeposit(common.SavepointCase):

    def setUp(self):
        super(TestStockDeposit, self).setUp()
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
        self.customer2 = self.env['res.partner'].create({
            'name': 'Customer - test - 2',
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

    def test_location_after_wh_create(self):
        location = self.Location.search([
            ('deposit_location', '=', True),
            ('location_id', '=', self.warehouse.lot_stock_id.id),
        ])
        self.assertEqual(len(location), 1)

    def test_picking_type_after_wh_create(self):
        picking_type = self.PickingType.search([
            ('warehouse_id', '=', self.warehouse.id),
            ('default_location_src_id', '=', self.warehouse.lot_stock_id.id),
            ('is_deposit', '=', True),
        ])
        self.assertEqual(len(picking_type), 1)
        self.assertTrue(picking_type.sequence_id)
        picking_type = self.PickingType.search([
            ('warehouse_id', '=', self.warehouse.id),
            ('default_location_src_id', '=', self.deposit_location.id),
            ('default_location_dest_id', '=', self.warehouse.lot_stock_id.id),
        ])
        self.assertEqual(len(picking_type), 1)
        self.assertTrue(picking_type.sequence_id)

    def test_picking_onchange_owner(self):
        picking = self._prepare_picking()
        picking.owner_id = self.customer2.id
        picking._onchange_owner_id()
        self.assertEqual(picking.partner_id.id, self.customer2.id)

    def test_picking_transfer_deposit(self):
        # Check qty after create inventory on hand
        qty_available = self.product.with_context(
            location=self.warehouse.lot_stock_id.id).qty_available
        self.assertEqual(qty_available, 200.00)
        picking = self._prepare_picking()
        picking.action_assign()
        picking.do_transfer()
        # Check qty after transfer goods to deposit location
        qty_available = self.product.with_context(
            warehouse=self.warehouse.id).qty_available
        self.assertEqual(qty_available, 180.00)
        self.assertEqual(self.product.with_context(
            location=self.deposit_location.id).deposit_available, 20.0)
        product = self.product.product_variant_ids[:1]
        result = product.deposit_action_open_quants()
        self.assertTrue(
            "'search_default_product_tmpl_id': %s" % self.product.id
            in result['context'])

    def test_deposit_regularize(self):
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
            'quants_action': 'regularize',
        }
        regularize = regularize_obj.with_context(
            active_ids=quants_to_regularize.ids,
        ).create(vals)
        # Check wizard lines
        self.assertEqual(len(regularize.line_ids), 1)
        self.assertEqual(regularize.line_ids.new_qty, 20)
        regularize.with_context(
            active_ids=regularize.line_ids.quant_id,
            warehouse=self.warehouse.id
        ).action_apply()
        qty_available = self.product.with_context(
            location=self.warehouse.lot_stock_id.id).qty_available
        self.assertEqual(qty_available, 180.00)
        self.assertEqual(self.product.with_context(
            location=self.deposit_location.id).deposit_available, 0.0)

    def test_deposit_regularize_more_qty(self):
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
            'quants_action': 'regularize',
        }
        regularize = regularize_obj.with_context(
            active_ids=quants_to_regularize.ids,
        ).create(vals)
        # Entry more units than allowed
        with self.assertRaises(ValidationError):
            regularize.line_ids.new_qty = 90.0
            regularize.with_context(
                active_ids=regularize.line_ids.quant_id,
                warehouse=self.warehouse.id
            ).action_apply()

    def _prepare_return_picking(self):
        picking_type = self.PickingType.search([
            ('warehouse_id', '=', self.warehouse.id),
            ('default_location_src_id', '=', self.deposit_location.id),
        ])
        picking = self.Picking.create({
            'name': 'picking - return - test 01',
            'location_id': self.deposit_location.id,
            'location_dest_id': self.warehouse.lot_stock_id.id,
            'owner_id': self.customer.id,
            'picking_type_id': picking_type.id,
            'move_lines': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.product_variant_ids[:1].id,
                'product_uom_qty': 10.0,
                'product_uom': self.product.uom_id.id,
                'restrict_partner_id': self.customer.id,
            })]
        })
        return picking

    def test_deposit_return(self):
        picking = self._prepare_picking()
        picking.action_assign()
        picking.do_transfer()

        picking_return = self._prepare_return_picking()
        picking_return.action_assign()
        picking_return.do_transfer()

        quants = self.env['stock.quant'].search([
            ('product_id', '=', self.product.product_variant_ids[:1].id),
            ('location_id', '=', self.deposit_location.id),
        ])
        self.assertEquals(quants.qty, 10.00)
