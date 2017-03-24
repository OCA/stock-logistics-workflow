# -*- coding: utf-8 -*-
# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.exceptions import UserError


class TestOperationQuickChange(TransactionCase):

    def setUp(self):
        super(TestOperationQuickChange, self).setUp()
        self.Location = self.env['stock.location']
        self.PickingType = self.env['stock.picking.type']
        self.Picking = self.env['stock.picking']
        self.Product = self.env['product.template']
        self.Wizard = self.env['stock.picking.operation.wizard']
        self.warehouse = self.env['stock.warehouse'].create({
            'name': 'warehouse - test',
            'code': 'WH-TEST',
        })

        # self.warehouse.lot_stock_id.id
        self.product = self.Product.create({
            'name': 'Product - Test',
            'type': 'product',
            'list_price': 100.00,
            'standard_price': 100.00,
        })
        self.qty_on_hand(self.product.product_variant_ids[:1])
        self.product2 = self.Product.create({
            'name': 'Product2 - Test',
            'type': 'product',
            'list_price': 100.00,
            'standard_price': 100.00,
        })
        self.qty_on_hand(self.product2.product_variant_ids[:1])
        self.customer = self.env['res.partner'].create({
            'name': 'Customer - test',
            'customer': True,
        })
        self.picking_type = self.PickingType.search([
            ('warehouse_id', '=', self.warehouse.id),
            ('code', '=', 'outgoing'),
        ])
        self.picking = self.Picking.create({
            'name': 'picking - test 01',
            'location_id': self.warehouse.lot_stock_id.id,
            'location_dest_id': self.warehouse.wh_output_stock_loc_id.id,
            'picking_type_id': self.picking_type.id,
            'move_lines': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.product_variant_ids[:1].id,
                'product_uom_qty': 20.0,
                'product_uom': self.product.uom_id.id,
            }), (0, 0, {
                'name': self.product.name,
                'product_id': self.product2.product_variant_ids[:1].id,
                'product_uom_qty': 60.0,
                'product_uom': self.product.uom_id.id,
            })]
        })

    def qty_on_hand(self, product):
        stock_change_obj = self.env['stock.change.product.qty']
        vals = {
            'product_id': product.id,
            'new_quantity': 200.0,
            'location_id': self.warehouse.lot_stock_id.id,
        }
        wiz = stock_change_obj.create(vals)
        wiz.change_product_qty()

    def test_picking_operation_change_location_dest_all(self):
        self.picking.action_assign()
        new_location_dest_id = self.Location.create({
            'name': 'New Test Customer Location',
            'location_id': self.picking.location_dest_id.location_id.id
        })
        wiz = self.Wizard.with_context(
            active_model=self.picking._name,
            active_ids=self.picking.ids,
        ).create({
            'new_location_dest_id': new_location_dest_id.id,
            'change_all': True,
        })
        operations = self.picking.mapped('pack_operation_product_ids')
        self.assertEqual(wiz.location_dest_id, self.picking.location_dest_id)
        self.assertEqual(wiz.old_location_dest_id,
                         operations[:1].location_dest_id)
        wiz.action_apply()
        operations = self.picking.mapped(
            'pack_operation_product_ids.location_dest_id')
        self.assertEqual(len(operations), 1)

    def test_picking_operation_change_location_dest(self):
        new_location_dest_id = self.Location.create({
            'name': 'New Test Customer Location',
            'location_id': self.picking.location_dest_id.location_id.id
        })
        other_location_dest_id = self.Location.create({
            'name': 'New Test Customer Location',
            'location_id': self.picking.location_dest_id.location_id.id
        })
        self.picking.action_assign()
        operations = self.picking.mapped('pack_operation_product_ids')
        operations[:1].write({'location_dest_id': other_location_dest_id.id})
        wiz = self.Wizard.with_context(
            active_model=self.picking._name,
            active_ids=self.picking.ids,
        ).create({
            'old_location_dest_id': self.picking.location_dest_id.id,
            'new_location_dest_id': new_location_dest_id.id,
        })
        wiz.action_apply()
        operations = self.picking.mapped(
            'pack_operation_product_ids.location_dest_id')
        self.assertEqual(len(operations), 2)

    def test_picking_operation_change_location_dest_failed(self):
        self.picking.action_assign()
        self.picking.action_done()
        new_location_dest_id = self.Location.create({
            'name': 'New Test Customer Location',
            'location_id': self.picking.location_dest_id.location_id.id
        })
        wiz = self.Wizard.with_context(
            active_model=self.picking._name,
            active_ids=self.picking.ids,
        ).create({
            'new_location_dest_id': new_location_dest_id.id,
            'change_all': True,
        })
        with self.assertRaises(UserError):
            wiz.action_apply()
