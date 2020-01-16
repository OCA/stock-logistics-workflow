# Copyright 2019 Tecnativa - Carlos Dauden
# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestProductCostPriceAvcoSync(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestProductCostPriceAvcoSync, cls).setUpClass()
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
        cls.product = cls.env['product.product'].create({
            'name': 'Product for test',
            'type': 'product',
            'tracking': 'none',
            'property_cost_method': 'average',
            'standard_price': 1,
        })
        cls.picking_in = cls.env['stock.picking'].create({
            'picking_type_id': cls.picking_type_in.id,
            'location_id': cls.supplier_location.id,
            'location_dest_id': cls.stock_location.id,
            'move_lines': [(0, 0, {
                'name': 'a move',
                'product_id': cls.product.id,
                'product_uom_qty': 10.0,
                'product_uom': cls.product.uom_id.id,
            })],
        })

        cls.picking_out = cls.env['stock.picking'].create({
            'picking_type_id': cls.picking_type_out.id,
            'location_id': cls.stock_location.id,
            'location_dest_id': cls.customer_location.id,
            'move_lines': [(0, 0, {
                'name': 'a move',
                'product_id': cls.product.id,
                'product_uom_qty': 5.0,
                'product_uom': cls.product.uom_id.id,
            })],
        })

    def test_sync_cost_price(self):
        move_in = self.picking_in.move_lines[:1]
        move_in.product_uom_qty = 100
        move_in.price_unit = 5.0
        move_in.quantity_done = move_in.product_uom_qty
        self.picking_in.action_done()
        move_in.date = '2019-10-01 00:00:00'

        picking_in_2 = self.picking_in.copy()
        move_in_2 = picking_in_2.move_lines[:1]
        move_in_2.product_uom_qty = 10.0
        move_in_2.quantity_done = move_in_2.product_uom_qty
        picking_in_2.action_done()
        move_in_2.date = '2019-10-02 00:00:00'

        move_out = self.picking_out.move_lines[:1]
        move_out.quantity_done = move_out.product_uom_qty
        self.picking_out.action_done()
        move_out.date = '2019-10-03 00:00:00'

        picking_out_2 = self.picking_out.copy()
        move_out_2 = picking_out_2.move_lines[:1]
        move_out_2.quantity_done = move_out_2.product_uom_qty
        picking_out_2.action_done()
        move_out_2.date = '2019-10-04 00:00:00'

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
        inventory._action_done()
        inventory.move_ids.date = '2019-10-05 00:00:00'

        self.assertEqual(self.product.standard_price, 5.0)
        move_in.price_unit = 2.0
        self.assertEqual(self.product.standard_price, 2.27)
        self.assertAlmostEqual(move_out.price_unit, -2.27, 2)
        self.assertAlmostEqual(move_out_2.price_unit, -2.27, 2)

    def test_sync_cost_price_and_history(self):
        company_id = self.picking_in.company_id.id
        move_in = self.picking_in.move_lines[:1]
        move_in.quantity_done = move_in.product_uom_qty
        self.picking_in.action_done()
        move_in.date = '2019-10-01 00:00:00'

        move_out = self.picking_out.move_lines[:1]
        move_out.quantity_done = move_out.product_uom_qty
        self.picking_out.action_done()
        move_out.date = '2019-10-01 01:00:00'

        picking_in_2 = self.picking_in.copy()
        move_in_2 = picking_in_2.move_lines[:1]
        move_in_2.quantity_done = move_in_2.product_uom_qty
        picking_in_2.action_done()
        move_in_2.date = '2019-10-01 02:00:00'

        picking_out_2 = self.picking_out.copy()
        move_out_2 = picking_out_2.move_lines[:1]
        move_out_2.product_uom_qty = 15
        move_out_2.quantity_done = move_out_2.product_uom_qty
        picking_out_2.action_done()
        move_out_2.date = '2019-10-01 03:00:00'

        picking_in_3 = self.picking_in.copy()
        move_in_3 = picking_in_3.move_lines[:1]
        move_in_3.quantity_done = move_in_3.product_uom_qty
        move_in_3.price_unit = 2.0
        picking_in_3.action_done()
        move_in_3.date = '2019-10-01 04:00:00'

        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)
        self.assertAlmostEqual(self.product.get_history_price(
            company_id), 2.0, 2)
        self.product.standard_price = 20.0
        self.assertAlmostEqual(self.product.get_history_price(
            company_id), 20.0, 2)

        move_in.price_unit = 10.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)
        self.assertAlmostEqual(move_out.price_unit, -10.0, 2)
        self.assertAlmostEqual(move_out_2.price_unit, -4.0, 2)
        self.assertAlmostEqual(self.product.get_history_price(
            company_id, move_in_3._previous_instant_date()), 4.0, 2)

        move_in_3.quantity_done = 5.0
        self.assertAlmostEqual(self.product.standard_price, 2.0, 2)
        move_in_3.quantity_done = 0.0
        self.assertAlmostEqual(self.product.standard_price, 4.0, 2)

        (move_in | move_in_2 | move_in_3).write({'price_unit': 9.0})
        self.assertAlmostEqual(self.product.standard_price, 9.0, 2)

        price_history_count = self.env['product.price.history'].search_count([
            ('company_id', '=', company_id),
            ('product_id', '=', self.product.id),
        ])
        self.assertEqual(price_history_count, 4)
