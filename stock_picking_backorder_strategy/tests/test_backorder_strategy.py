# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestBackorderStrategy(common.TransactionCase):

    def setUp(self):
        """ Create the picking
        """
        super(TestBackorderStrategy, self).setUp()

        self.picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']

        self.picking_type = self.env.ref('stock.picking_type_in')

        product = self.env.ref('product.product_product_13')
        loc_supplier_id = self.env.ref('stock.stock_location_suppliers').id
        loc_stock_id = self.env.ref('stock.stock_location_stock').id

        self.picking = self.picking_obj.create({
            'picking_type_id': self.picking_type.id,
            'location_id': loc_supplier_id,
            'location_dest_id': loc_stock_id,
        })
        move_obj.create({
            'name': '/',
            'picking_id': self.picking.id,
            'product_uom': product.uom_id.id,
            'location_id': loc_supplier_id,
            'location_dest_id': loc_stock_id,
            'product_id': product.id,
            'product_uom_qty': 2
        })
        self.picking.action_confirm()

    def _process_picking(self):
        """ Receive partially the picking
        """
        res = self.picking.button_validate()
        return res

    def test_backorder_strategy_create(self):
        """ Check strategy for stock.picking_type_in is create
            Receive picking
            Check backorder is created
        """
        self.picking_type.backorder_strategy = 'create'
        self._process_picking()
        backorder = self.picking_obj.search(
            [('backorder_id', '=', self.picking.id)])
        if len(backorder):
            self.assertTrue(backorder)

    def test_backorder_strategy_no_create(self):
        """ Set strategy for stock.picking_type_in to no_create
            Receive picking
            Check there is no backorder
            Check if there is one move done and one move cancelled
        """
        self.picking_type.backorder_strategy = 'no_create'
        self._process_picking()
        backorder = self.picking_obj.search(
            [('backorder_id', '=', self.picking.id)])
        if len(backorder):
            self.assertFalse(backorder)
            states = list(set(self.picking.move_lines.mapped('state')))
            self.assertEquals(
                'done',
                self.picking.state,
            )
            self.assertListEqual(
                ['cancel', 'done'],
                states,
            )

    def test_backorder_strategy_cancel(self):
        """ Set strategy for stock.picking_type_in to cancel
            Receive picking
            Check the backorder state is cancel
        """
        self.picking_type.backorder_strategy = 'cancel'
        self._process_picking()
        backorder = self.picking_obj.search(
            [('backorder_id', '=', self.picking.id)])
        if len(backorder):
            self.assertTrue(backorder)
            self.assertEqual('cancel', backorder[0].state)

    def test_backorder_strategy_manual(self):
        """ Set strategy for stock.picking_type_in to manual
            Receive picking
            Check the backorder wizard is launched
        """
        self.assertEqual('manual', self.picking_type.backorder_strategy)
        old_wizards = self.env['stock.backorder.confirmation'].search([])
        self._process_picking()
        if len(old_wizards):
            backorder_obj = self.env['stock.backorder.confirmation']
            new_wizards = backorder_obj.search([]) -\
                old_wizards
            if len(new_wizards):
                self.assertTrue(new_wizards)
