# -*- coding: utf-8 -*-
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common


@common.at_install(False)
@common.post_install(True)
class TestStockPickingTransferLotAutoAssign(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockPickingTransferLotAutoAssign, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test partner'})
        cls.warehouse = cls.env['stock.warehouse'].search([], limit=1)
        cls.picking_type = cls.env['stock.picking.type'].search([
            ('warehouse_id', '=', cls.warehouse.id),
            ('code', '=', 'outgoing'),
        ], limit=1)
        cls.picking = cls.env['stock.picking'].create({
            'partner_id': cls.partner.id,
            'picking_type_id': cls.picking_type.id,
            'location_id': cls.picking_type.default_location_src_id.id,
            'location_dest_id': cls.partner.property_stock_customer.id,
        })
        cls.Move = cls.env['stock.move']
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
            'type': 'product',
            'tracking': 'lot',
        })
        cls.product_no_lot = cls.env['product.product'].create({
            'name': 'Test product no lot',
            'type': 'product',
            'tracking': 'none',
        })
        cls.lot1 = cls.env['stock.production.lot'].create({
            'product_id': cls.product.id,
            'name': 'Lot 1',
        })
        cls.quant1 = cls.env['stock.quant'].create({
            'product_id': cls.product.id,
            'location_id': cls.picking.location_id.id,
            'qty': 6,
            'lot_id': cls.lot1.id,
        })
        cls.lot2 = cls.env['stock.production.lot'].create({
            'product_id': cls.product.id,
            'name': 'Lot 2',
        })
        cls.quant2 = cls.env['stock.quant'].create({
            'product_id': cls.product.id,
            'location_id': cls.picking.location_id.id,
            'qty': 10,
            'lot_id': cls.lot2.id,
        })
        cls.quant_no_lot = cls.env['stock.quant'].create({
            'product_id': cls.product_no_lot.id,
            'location_id': cls.picking.location_id.id,
            'qty': 10,
        })
        move_vals = cls.Move.onchange_product_id(
            prod_id=cls.product.id,
            loc_id=cls.picking.location_id.id,
            loc_dest_id=cls.picking.location_dest_id.id,
            partner_id=cls.picking.partner_id.id,
        ).get('value', {})
        move_vals.update({
            'product_id': cls.product.id,
            'picking_id': cls.picking.id,
            'product_uom_qty': 10,
        })
        cls.move = cls.Move.create(move_vals)

    def test_transfer(self):
        self.picking.action_confirm()
        self.picking.action_assign()
        pack_ops = self.picking.pack_operation_ids
        self.assertEqual(len(pack_ops), 1)
        self.assertEqual(len(pack_ops.pack_lot_ids), 2)
        self.assertEqual(pack_ops.pack_lot_ids[0].qty, 6)
        self.assertEqual(pack_ops.pack_lot_ids[1].qty, 4)
        self.assertEqual(pack_ops.qty_done, 10)

    def test_autocomplete_backorder(self):
        """Adds move with a product with 'none' lot track"""
        move_vals = self.Move.onchange_product_id(
            prod_id=self.product_no_lot.id,
            loc_id=self.picking.location_id.id,
            loc_dest_id=self.picking.location_dest_id.id,
            partner_id=self.picking.partner_id.id,
        ).get('value', {})
        move_vals.update({
            'product_id': self.product_no_lot.id,
            'picking_id': self.picking.id,
            'product_uom_qty': 10,
        })
        self.move = self.Move.create(move_vals)
        self.picking.action_confirm()
        self.picking.action_assign()
        backorder_wiz_view = self.picking.do_new_transfer()
        backorder_wiz = self.env['stock.backorder.confirmation'].browse(
            backorder_wiz_view.get('res_id'))
        backorder_wiz.process_assign_ordered_qty()
        pack_ops = self.picking.pack_operation_ids

        self.assertEqual(len(pack_ops), 2)
        self.assertEqual(pack_ops[1].qty_done, 10)
