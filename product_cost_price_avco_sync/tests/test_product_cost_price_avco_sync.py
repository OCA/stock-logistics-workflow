# Copyright 2019 Tecnativa - Carlos Dauden
# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestProductCostPriceAvcoSync(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestProductCostPriceAvcoSync, cls).setUpClass()
        cls.PurchaseOrder = cls.env['purchase.order']
        cls.StockPicking = cls.env['stock.picking']
        cls.supplier_location = cls.env.ref('stock.stock_location_suppliers')
        cls.customer_location = cls.env.ref('stock.stock_location_customers')
        cls.warehouse = cls.env.ref('stock.warehouse0')
        cls.stock_location = cls.env.ref('stock.stock_location_stock')
        cls.picking_type_in = cls.env.ref('stock.picking_type_in')
        cls.picking_type_out = cls.env.ref('stock.picking_type_out')
        cls.partner = cls.env['res.partner'].create({
            'customer': True,
            'supplier': True,
            'name': 'Test Partner',
        })
        cls.picking = cls.env['stock.picking'].create({
            'picking_type_id': cls.picking_type_in.id,
            'location_id': cls.supplier_location.id,
            'location_dest_id': cls.stock_location.id,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product for test',
            'type': 'product',
            'tracking': 'none',
            'property_cost_method': 'average',
        })
        cls.env['stock.move'].create({
            'name': 'a move',
            'product_id': cls.product.id,
            'product_uom_qty': 5.0,
            'product_uom': cls.product.uom_id.id,
            'picking_id': cls.picking.id,
            'location_id': cls.supplier_location.id,
            'location_dest_id': cls.stock_location.id,
        })
        cls.picking.action_assign()
        cls.move_line = cls.picking.move_lines[:1]

    def test_sync_cost_price(self):
        po = self.env['purchase.order'].new({
            'partner_id': self.partner.id,
            'date_order': '2019-10-01',
        })
        default_vals = self.PurchaseOrder.default_get(
            list(self.PurchaseOrder._fields))
        po.update(default_vals)
        po.onchange_partner_id()
        po.order_line = [(0, 0, {
            'product_id': self.product.id,
        })]
        po.order_line.onchange_product_id()
        po.order_line.product_qty = 100.0
        po.order_line.price_unit = 5.0
        purchase_order = self.PurchaseOrder.create(
            po._convert_to_write(po._cache))
        purchase_order.button_confirm()
        purchase_order.picking_ids.move_line_ids.qty_done = 100.0
        purchase_order.picking_ids.action_done()
        purchase_order.picking_ids.move_lines.date = '2019-10-01'

        picking_in_vals = {
            'name': '/',
            'partner_id': self.partner.id,
            'picking_type_id': self.picking_type_in.id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'move_lines': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 10.0,
                'product_uom': self.product.uom_id.id,
                'location_id': self.supplier_location.id,
                'location_dest_id': self.stock_location.id,
            })]
        }
        picking_in = self.StockPicking.create(picking_in_vals)
        picking_in.move_line_ids.qty_done = 10.0
        picking_in.action_done()
        picking_in.move_lines.date = '2019-10-02'

        picking_out_vals = {
            'name': '/',
            'partner_id': self.partner.id,
            'picking_type_id': self.picking_type_out.id,
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id,
            'move_lines': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 10.0,
                'product_uom': self.product.uom_id.id,
                'location_id': self.stock_location.id,
                'location_dest_id': self.customer_location.id,
            })]
        }

        picking_out = self.StockPicking.create(picking_out_vals.copy())
        picking_out.action_assign()
        picking_out.move_line_ids.qty_done = 5.0
        picking_out.action_done()
        picking_out.move_lines.date = '2019-10-03'

        picking_out2 = self.StockPicking.create(picking_out_vals.copy())
        picking_out2.action_assign()
        picking_out2.move_line_ids.qty_done = 5.0
        picking_out2.action_done()
        picking_out2.move_lines.date = '2019-10-04'

        # Make an inventory
        inventory = self.env['stock.inventory'].create({
            'name': 'Initial inventory',
            'filter': 'partial',
            'location_id': self.warehouse.lot_stock_id.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_id': self.product.uom_id.id,
                'product_qty': 200,
                'location_id': self.warehouse.lot_stock_id.id
            })]
        })
        inventory.action_done()
        inventory.move_ids.date = '2019-10-05'

        self.assertEqual(self.product.standard_price, 5.0)
        purchase_order.order_line.price_unit = 2.0
        self.assertEqual(self.product.standard_price, 2.27)
        self.assertAlmostEqual(
            round(picking_out.move_lines.price_unit, 2), -2.27)
        self.assertAlmostEqual(
            round(picking_out2.move_lines.price_unit, 2), -2.27)
