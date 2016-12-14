# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestProcurement(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestProcurement, cls).setUpClass()

        cls.customer = cls.env['res.partner'].search(
            [('customer', '=', True)], limit=1)

        cls.supplier = cls.env['res.partner'].search(
            [('supplier', '=', True)], limit=1)

        cls.customer_location = cls.env.ref(
            'stock.stock_location_customers')

        cls.supplier_location = cls.env.ref(
            'stock.stock_location_suppliers')

        cls.dropship_route = cls.env['stock.location.route'].create({
            'name': 'Dropship',
            'product_selectable': True,
        })
        cls.buy_route = cls.env['stock.location.route'].create({
            'name': 'Buy',
            'product_selectable': True,
        })

        cls.warehouse = cls.env['stock.warehouse'].create({
            'name': 'Main Warehouse',
            'code': 'MWH',
        })

        cls.sequence = cls.env['ir.sequence'].search([], limit=1)

        cls.picking_type = cls.env['stock.picking.type'].create({
            'name': 'Dropship',
            'code': 'incoming',
            'sequence_id': cls.sequence.id,
        })

        cls.dropship_rule = cls.env['procurement.rule'].create({
            'name': 'Dropship',
            'procure_method': 'make_to_order',
            'action': 'buy',
            'location_id': cls.customer_location.id,
            'location_src_id': cls.supplier_location.id,
            'route_id': cls.dropship_route.id,
            'picking_type_id': cls.picking_type.id,
        })

        cls.buy_step_1 = cls.env['procurement.rule'].create({
            'name': 'Buy Step 1',
            'procure_method': 'make_to_order',
            'action': 'buy',
            'location_id': cls.warehouse.lot_stock_id.id,
            'location_src_id': cls.supplier_location.id,
            'route_id': cls.buy_route.id,
            'picking_type_id': cls.picking_type.id,
        })

        cls.buy_step_2 = cls.env['procurement.rule'].create({
            'name': 'Buy Step 2',
            'procure_method': 'make_to_order',
            'action': 'move',
            'location_id': cls.customer_location.id,
            'location_src_id': cls.warehouse.lot_stock_id.id,
            'route_id': cls.buy_route.id,
            'picking_type_id': cls.picking_type.id,
        })

        cls.product = cls.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'seller_ids': [(0, 0, {'name': cls.supplier.id})],
        })
        cls.product.categ_id.route_ids = False

        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.customer.id,
        })

        cls.order_line = cls.env['sale.order.line'].create({
            'product_id': cls.product.id,
            'order_id': cls.sale_order.id,
            'product_uom_qty': 1,
            'price_unit': 1000.00,
        })

    def test_01_sale_confirm_exception(self):
        self.product.route_ids = self.dropship_route | self.buy_route
        self.sale_order.action_confirm()
        procurement = self.order_line.procurement_ids
        self.assertEqual(procurement.state, 'exception')

        procurement.product_route_id = self.buy_route
        procurement.run()
        self.assertEqual(procurement.state, 'running')
        self.assertEqual(procurement.rule_id, self.buy_step_2)

    def test_02_sale_confirm_single_route(self):
        self.product.route_ids = self.dropship_route
        self.sale_order.action_confirm()
        procurement = self.order_line.procurement_ids
        self.assertEqual(procurement.state, 'running')
        self.assertEqual(procurement.rule_id, self.dropship_rule)
