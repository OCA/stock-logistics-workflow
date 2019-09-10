# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class StockReturnRequestCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_obj = cls.env['product.product']
        cls.prod_1 = cls.product_obj.create({
            'name': 'Test Product 1',
            'type': 'product',
        })
        cls.prod_2 = cls.prod_1.copy({
            'name': 'Test Product 2',
            'type': 'product',
        })
        cls.prod_3 = cls.prod_1.copy({
            'name': 'Test Product 3',
            'type': 'product',
            'tracking': 'lot',
        })
        cls.prod_3_lot1 = cls.env['stock.production.lot'].create({
            'name': 'TSTPROD3LOT0001',
            'product_id': cls.prod_3.id,
        })
        cls.prod_3_lot2 = cls.prod_3_lot1.copy({
            'name': 'TSTPROD3LOT0002',
        })
        cls.wh1 = cls.env['stock.warehouse'].create({
            'name': 'TEST WH1',
            'code': 'TST1',
        })
        # Locations (WH1 locations are created automatically)
        location_obj = cls.env['stock.location']
        cls.supplier_loc = location_obj.create({
            'name': 'Test supplier location',
            'usage': 'supplier',
        })
        cls.customer_loc = location_obj.create({
            'name': 'Test customer location',
            'usage': 'customer',
        })
        # Create partners
        cls.partner_customer = cls.env['res.partner'].create({
            'name': 'Mr. Odoo',
            'property_stock_supplier': cls.supplier_loc.id,
            'property_stock_customer': cls.customer_loc.id,
        })
        cls.partner_supplier = cls.env['res.partner'].create({
            'name': 'Mrs. OCA',
            'property_stock_supplier': cls.supplier_loc.id,
            'property_stock_customer': cls.customer_loc.id,
        })
        # Create deliveries and receipts orders to have a history
        # First, some incoming pickings
        cls.picking_obj = cls.env['stock.picking']
        cls.picking_supplier_1 = cls.picking_obj.create({
            'location_id': cls.supplier_loc.id,
            'location_dest_id': cls.wh1.lot_stock_id.id,
            'partner_id': cls.partner_supplier.id,
            'picking_type_id': cls.wh1.in_type_id.id,
            'move_lines': [
                (0, 0, {
                    'name': cls.prod_1.name,
                    'product_id': cls.prod_1.id,
                    'product_uom_qty': 10.0,
                    'product_uom': cls.prod_1.uom_id.id,
                    'quantity_done': 10.0,
                }),
                (0, 0, {
                    'name': cls.prod_2.name,
                    'product_id': cls.prod_2.id,
                    'product_uom_qty': 20.0,
                    'product_uom': cls.prod_2.uom_id.id,
                    'quantity_done': 20.0,
                }),
                (0, 0, {
                    'name': cls.prod_3.name,
                    'product_id': cls.prod_3.id,
                    'product_uom_qty': 30.0,
                    'product_uom': cls.prod_3.uom_id.id,
                })],
        })
        move3 = cls.picking_supplier_1.move_lines.filtered(
            lambda x: x.product_id == cls.prod_3)
        move3.write({
            'move_line_ids': [
                (0, 0, {
                    'picking_id': cls.picking_supplier_1.id,
                    'lot_id': cls.prod_3_lot1.id,
                    'product_id': cls.prod_3.id,
                    'product_uom_id': cls.prod_3.uom_id.id,
                    'location_id': cls.supplier_loc.id,
                    'location_dest_id': cls.wh1.lot_stock_id.id,
                    'qty_done': 20,
                }),
                (0, 0, {
                    'picking_id': cls.picking_supplier_1.id,
                    'product_id': cls.prod_3.id,
                    'product_uom_id': cls.prod_3.uom_id.id,
                    'lot_id': cls.prod_3_lot2.id,
                    'location_id': cls.supplier_loc.id,
                    'location_dest_id': cls.wh1.lot_stock_id.id,
                    'qty_done': 10,
                }),
            ],
        })
        move3.qty_done = 30
        cls.picking_supplier_1.action_confirm()
        cls.picking_supplier_1.action_assign()
        cls.picking_supplier_1.action_done()
        cls.picking_supplier_2 = cls.picking_supplier_1.copy({
            'move_lines': [
                (0, 0, {
                    'name': cls.prod_1.name,
                    'product_id': cls.prod_1.id,
                    'product_uom_qty': 90.0,
                    'product_uom': cls.prod_1.uom_id.id,
                    'quantity_done': 90.0,
                }),
                (0, 0, {
                    'name': cls.prod_2.name,
                    'product_id': cls.prod_2.id,
                    'product_uom_qty': 80.0,
                    'product_uom': cls.prod_2.uom_id.id,
                    'quantity_done': 90.0,
                }),
                (0, 0, {
                    'name': cls.prod_3.name,
                    'product_id': cls.prod_3.id,
                    'product_uom_qty': 70.0,
                    'product_uom': cls.prod_3.uom_id.id,
                })],
        })
        move3 = cls.picking_supplier_2.move_lines.filtered(
            lambda x: x.product_id == cls.prod_3)
        move3.write({
            'move_line_ids': [
                (0, 0, {
                    'picking_id': cls.picking_supplier_2.id,
                    'lot_id': cls.prod_3_lot1.id,
                    'product_id': cls.prod_3.id,
                    'product_uom_id': cls.prod_3.uom_id.id,
                    'location_id': cls.supplier_loc.id,
                    'location_dest_id': cls.wh1.lot_stock_id.id,
                    'qty_done': 70,
                }),
            ],
        })
        move3.qty_done = 30
        cls.picking_supplier_2.action_confirm()
        cls.picking_supplier_2.action_assign()
        cls.picking_supplier_2.action_done()
        # We'll have 100 units of each product
        # No we deliver some products
        cls.picking_customer_1 = cls.picking_obj.create({
            'location_id': cls.wh1.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'partner_id': cls.partner_customer.id,
            'picking_type_id': cls.wh1.out_type_id.id,
            'move_lines': [
                (0, 0, {
                    'name': cls.prod_1.name,
                    'product_id': cls.prod_1.id,
                    'product_uom_qty': 10.0,
                    'product_uom': cls.prod_1.uom_id.id,
                    'quantity_done': 10.0,
                }),
                (0, 0, {
                    'name': cls.prod_2.name,
                    'product_id': cls.prod_2.id,
                    'product_uom_qty': 20.0,
                    'product_uom': cls.prod_2.uom_id.id,
                    'quantity_done': 20.0,
                })],
        })
        cls.picking_customer_1.action_confirm()
        cls.picking_customer_1.action_assign()
        cls.picking_customer_1.action_done()
        cls.picking_customer_2 = cls.picking_customer_1.copy({
            'move_lines': [
                (0, 0, {
                    'name': cls.prod_1.name,
                    'product_id': cls.prod_1.id,
                    'product_uom_qty': 10.0,
                    'product_uom': cls.prod_1.uom_id.id,
                    'quantity_done': 10.0,
                }),
                (0, 0, {
                    'name': cls.prod_2.name,
                    'product_id': cls.prod_2.id,
                    'product_uom_qty': 10.0,
                    'product_uom': cls.prod_2.uom_id.id,
                    'quantity_done': 10.0,
                })],
        })
        cls.picking_customer_2.action_confirm()
        cls.picking_customer_2.action_assign()
        cls.picking_customer_2.action_done()
        # Stock in wh1.lot_stock_id
        # prod_1: 80.0 / prod_2: 70.0 / prod_3: 100.0
        cls.return_request_obj = cls.env['stock.return.request']
        # Return from customer
        cls.return_request_customer = cls.return_request_obj.create({
            'partner_id': cls.partner_customer.id,
            'return_type': 'customer',
            'return_to_location': cls.wh1.lot_stock_id.id,
            'return_from_location': cls.wh1.lot_stock_id.id,
            'return_order': 'date desc, id desc',  # Newer first
        })
        cls.return_request_customer.onchange_locations()
        cls.return_request_supplier = cls.return_request_customer.copy({
            'partner_id': cls.partner_supplier.id,
            'return_to_location': cls.wh1.lot_stock_id.id,
            'return_from_location': cls.wh1.lot_stock_id.id,
            'return_type': 'supplier',
            'return_order': 'date asc, id desc',  # Older first
        })
        cls.return_request_supplier.onchange_locations()
