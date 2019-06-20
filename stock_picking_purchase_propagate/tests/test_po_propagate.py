# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests import SavepointCase


class TestPoPropagate(SavepointCase):

    @classmethod
    def setUpClass(cls):

        def _create_product(name, supplier):
            product_tmpl_model = cls.env['product.template']
            return product_tmpl_model.with_context(
                tracking_disable=True).create({
                    'name': name,
                    'type': 'product',
                    'purchase_ok': True,
                    'seller_ids': [(0, 0, {
                        'name': supplier.id,
                        'min_qty': 1,
                        'price': 1.0,
                    })],
                }).product_variant_ids

        def _create_orderpoint(product, qty_min, qty_max):
            orderpoint_model = cls.env['stock.warehouse.orderpoint']
            return orderpoint_model.create({
                'name': 'OP/%s' % product.name,
                'product_id': product.id,
                'product_min_qty': qty_min,
                'product_max_qty': qty_max,
            })

        super().setUpClass()

        cls.warehouse = cls.env.ref('stock.warehouse0')
        cls.stock_loc = cls.warehouse.lot_stock_id
        cls.input_loc = cls.warehouse.wh_input_stock_loc_id
        cls.qc_loc = cls.warehouse.wh_qc_stock_loc_id

        cls.internal_picking_type = cls.env.ref('stock.picking_type_internal')

        # Create suppliers
        partner_model = cls.env['res.partner'].with_context(
            tracking_disable=True)
        cls.strings_inc = partner_model.create({
            'name': 'Strings Inc',
            'company_type': 'company'
        })
        cls.drummers_friend = partner_model.create({
            'name': 'Drummers Friend',
            'company_type': 'company'
        })
        cls.piano_store = partner_model.create({
            'name': 'Piano store',
            'company_type': 'company'
        })
        # Create basic products
        cls.guitar = _create_product('Guitar', cls.strings_inc)
        cls.bass = _create_product('Bass', cls.strings_inc)
        cls.drumset = _create_product('Drumset', cls.drummers_friend)
        cls.piano = _create_product('Piano', cls.piano_store)
        cls.violin = _create_product('Violin', cls.strings_inc)
        # Create orderpoints
        cls.guitar_op = _create_orderpoint(cls.guitar, 20, 30)
        cls.bass_op = _create_orderpoint(cls.bass, 10, 15)
        cls.drumset_op = _create_orderpoint(cls.drumset, 5, 10)
        cls.piano_op = _create_orderpoint(cls.piano, 5, 10)

    def test_two_steps(self):
        self.warehouse.write({'reception_steps': 'two_steps'})
        self.env['procurement.group'].run_scheduler()

        # At the moment, the scheduler should have created one picking from
        # Input to stock with the three products and two PO
        internal_picking = self.env['stock.picking'].search(
            [('location_id', '=', self.input_loc.id)])
        internal_picking_moves = internal_picking.move_lines
        internal_picking_products = internal_picking_moves.mapped(
            'product_id')
        self.assertIn(self.guitar, internal_picking_products)
        self.assertIn(self.bass, internal_picking_products)
        self.assertIn(self.drumset, internal_picking_products)

        po_strings = self.env['purchase.order'].search(
            [('partner_id', '=', self.strings_inc.id)])
        po_drummers = self.env['purchase.order'].search(
            [('partner_id', '=', self.drummers_friend.id)])
        self.assertEqual(len(po_strings), 1)
        self.assertEqual(len(po_drummers), 1)

        # Confirming the PO will propagate PO procurement group to the ensuing
        # moves of the generated receipts, and reassign a picking according to
        # the new PG
        po_strings.button_confirm()
        receipt_picking = po_strings.picking_ids
        self.assertEqual(receipt_picking.partner_id, po_strings.partner_id)
        self.assertEqual(receipt_picking.location_dest_id, self.input_loc)
        po_procurement_group = receipt_picking.group_id
        receipt_moves = receipt_picking.move_lines
        for rm in receipt_moves:
            self.assertEqual(rm.group_id, po_procurement_group)
        receipt_products = receipt_moves.mapped('product_id')
        self.assertIn(self.guitar, receipt_products)
        self.assertIn(self.bass, receipt_products)
        internal_picking_products = internal_picking.move_lines.mapped(
            'product_id')
        self.assertNotIn(self.guitar, internal_picking_products)
        self.assertNotIn(self.bass, internal_picking_products)
        internal_moves = receipt_moves.mapped('move_dest_ids')
        for im in internal_moves:
            self.assertEqual(im.group_id, po_procurement_group)
        new_internal_picking = internal_moves.mapped('picking_id')
        self.assertNotEqual(new_internal_picking, internal_picking)

        # A reduced quantity on the PO will also get propagated
        self.assertEqual(len(po_drummers.order_line), 1)
        self.assertAlmostEqual(po_drummers.order_line.product_qty, 10.0)
        po_drummers.order_line.write({
            'product_qty': 3.0
        })
        po_drummers.button_confirm()
        receipt_picking = po_drummers.picking_ids
        self.assertEqual(receipt_picking.location_dest_id, self.input_loc)
        self.assertEqual(len(receipt_picking.move_lines), 1)
        self.assertEqual(receipt_picking.move_lines.product_id, self.drumset)
        self.assertAlmostEqual(receipt_picking.move_lines.product_uom_qty, 3.0)
        internal_move = receipt_picking.move_lines.move_dest_ids
        self.assertEqual(internal_move.location_id, self.input_loc)
        self.assertEqual(internal_move.location_dest_id, self.stock_loc)
        self.assertAlmostEqual(internal_move.product_uom_qty, 3.0)

        # As the qty above is below stock min for drumset product, ensure the
        # qty difference need is regenerated by the scheduler on the
        # same internal picking without procurement group
        self.assertNotIn(self.drumset,
                         internal_picking.move_lines.mapped('product_id'))
        self.env['procurement.group'].run_scheduler()
        self.assertIn(self.drumset,
                      internal_picking.move_lines.mapped('product_id'))
        drums_line = internal_picking.move_lines.filtered(
            lambda ml: ml.product_id == self.drumset)
        self.assertAlmostEqual(drums_line.product_uom_qty, 7.0)

    def test_three_steps(self):
        self.warehouse.write({'reception_steps': 'three_steps'})
        self.env['procurement.group'].run_scheduler()
        input_to_qc_picking = self.env['stock.picking'].search([
            ('location_id', '=', self.input_loc.id),
            ('location_dest_id', '=', self.qc_loc.id)
        ])
        qc_to_stock_picking = self.env['stock.picking'].search([
            ('location_id', '=', self.qc_loc.id),
            ('location_dest_id', '=', self.stock_loc.id)
        ])
        input_to_qc_picking_products = input_to_qc_picking.move_lines.mapped(
            'product_id')
        qc_to_stock_picking_products = qc_to_stock_picking.move_lines.mapped(
            'product_id')
        self.assertIn(self.guitar, input_to_qc_picking_products)
        self.assertIn(self.bass, input_to_qc_picking_products)
        self.assertIn(self.drumset, input_to_qc_picking_products)
        self.assertIn(self.guitar, qc_to_stock_picking_products)
        self.assertIn(self.bass, qc_to_stock_picking_products)
        self.assertIn(self.drumset, qc_to_stock_picking_products)

        po_drummers = self.env['purchase.order'].search(
            [('partner_id', '=', self.drummers_friend.id)])
        self.assertEqual(len(po_drummers.order_line), 1)
        self.assertAlmostEqual(po_drummers.order_line.product_qty, 10.0)
        po_drummers.order_line.write({
            'product_qty': 3.0
        })
        po_drummers.button_confirm()
        input_to_qc_picking_products = input_to_qc_picking.move_lines.mapped(
            'product_id')
        qc_to_stock_picking_products = qc_to_stock_picking.move_lines.mapped(
            'product_id')
        self.assertNotIn(self.drumset, input_to_qc_picking_products)
        self.assertNotIn(self.drumset, qc_to_stock_picking_products)

        receipt_picking = po_drummers.picking_ids
        po_procurement_group = receipt_picking.group_id
        self.assertEqual(len(receipt_picking), 1)
        receipt_move = receipt_picking.move_lines
        self.assertEqual(len(receipt_move), 1)
        self.assertEqual(receipt_move.product_id, self.drumset)
        self.assertAlmostEqual(receipt_move.product_uom_qty, 3.0)
        input_to_qc_move = receipt_move.move_dest_ids
        self.assertEqual(input_to_qc_move.location_id, self.input_loc)
        self.assertEqual(input_to_qc_move.location_dest_id, self.qc_loc)
        self.assertEqual(input_to_qc_move.group_id, po_procurement_group)
        self.assertEqual(input_to_qc_move.picking_id.group_id,
                         po_procurement_group)
        self.assertAlmostEqual(input_to_qc_move.product_uom_qty, 3.0)
        qc_to_stock_move = input_to_qc_move.move_dest_ids
        self.assertEqual(qc_to_stock_move.location_id, self.qc_loc)
        self.assertEqual(qc_to_stock_move.location_dest_id, self.stock_loc)
        self.assertEqual(qc_to_stock_move.group_id, po_procurement_group)
        self.assertEqual(qc_to_stock_move.picking_id.group_id,
                         po_procurement_group)
        self.assertAlmostEqual(qc_to_stock_move.product_uom_qty, 3.0)

    def test_two_warehouses_orderpoints(self):
        self.warehouse.write({'reception_steps': 'three_steps'})
        # Create second warehouse
        wh2 = self.env['stock.warehouse'].create({
            'name': 'WH2',
            'code': 'WH2',
            'partner_id': False
        })
        # Force parent store computation after creation of WH2 because location
        # quantities are computed using parent_left _right in domain
        self.env['stock.location']._parent_store_compute()
        # Create WH > WH2 PG and route
        wh_wh2_pg = self.env['procurement.group'].create({
            'name': 'WH > WH2',
            'move_type': 'direct'
        })
        wh_wh2_route = self.env['stock.location.route'].create({
            'name': 'WH > WH2',
            'product_selectable': True,
            'rule_ids': [(0, 0, {
                'name': 'WH>WH2',
                'action': 'pull',
                'location_id': wh2.lot_stock_id.id,
                'location_src_id': self.stock_loc.id,
                'procure_method': 'make_to_order',
                'picking_type_id': self.internal_picking_type.id,
                'group_propagation_option': 'fixed',
                'group_id': wh_wh2_pg.id,
                'propagate': True
            })]
        })
        # Add the new route to piano product
        self.piano.write({
            'route_ids': [(4, wh_wh2_route.id)]
        })
        self.piano_op.copy({
            'name': 'OP/%s-2' % self.piano.name,
            'location_id': wh2.lot_stock_id.id
        })
        self.env['procurement.group'].run_scheduler()
        # Ensure we get two internal moves to WH/Stock, one for each OP
        piano_moves_to_wh = self.env['stock.move'].search([
            ('product_id', '=', self.piano.id),
            ('location_dest_id', '=', self.stock_loc.id)
        ])
        self.assertEqual(len(piano_moves_to_wh), 2)
        for move in piano_moves_to_wh:
            self.assertAlmostEqual(move.product_uom_qty, 10.0)
            if move.picking_id.origin == 'WH > WH2':
                self.assertEqual(move.picking_id.group_id, wh_wh2_pg)
            else:
                self.assertFalse(move.picking_id.group_id)

        # Ensure PO was generated with one line for each OP
        po_pianos = self.env['purchase.order'].search(
            [('partner_id', '=', self.piano_store.id)])
        self.assertEqual(len(po_pianos.order_line), 2)
        for line in po_pianos.order_line:
            self.assertAlmostEqual(line.product_qty, 10.0)
            # Reduce qty on the line without PG.
            if not line.procurement_group_id:
                line.write({'product_qty': 6.0})
        po_pianos.button_confirm()
        for move in piano_moves_to_wh:
            if move.group_id == wh_wh2_pg:
                self.assertAlmostEqual(move.product_uom_qty, 10.0)
            else:
                self.assertAlmostEqual(move.product_uom_qty, 6.0)
                self.assertEqual(move.group_id.name, po_pianos.name)

    def test_manual_po(self):
        po = self.env['purchase.order'].create({
            'partner_id': self.strings_inc.id,
            'order_line': [
                (0, 0, {
                    'name': self.violin.name,
                    'product_id': self.violin.id,
                    'product_qty': 1.0,
                    'product_uom': self.violin.uom_po_id.id,
                    'price_unit': 10.0,
                    'date_planned': fields.Date.today(),
                })],
        })
        po.button_confirm()
