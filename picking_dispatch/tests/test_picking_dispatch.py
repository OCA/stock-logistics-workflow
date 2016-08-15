from openerp.tests import TransactionCase


class TestPickingDispatch(TransactionCase):

    def setUp(self):
        super(TestPickingDispatch, self).setUp()
        self.picking_dispatch_model = self.env['picking.dispatch']
        picking_model = self.env['stock.picking']

        self.stock_move = self.env.ref('stock.incomming_shipment_icecream')

        ref = self.ref
        self.picking = picking_model.create({
            'picking_type_id': self.ref('stock.picking_type_out'),
            'location_dest_id': ref('stock.stock_location_customers'),
            'move_lines': [
                (0, 0, {'name': 'move1',
                        'product_id': ref('product.product_product_6'),
                        'product_uom': ref('product.product_uom_unit'),
                        'product_uom_qty': 1,
                        'location_id': ref('stock.stock_location_stock'),
                        'location_dest_id':
                            ref('stock.stock_location_customers')
                        }
                 ),
                (0, 0, {'name': 'move2',
                        'product_id': ref('product.product_product_7'),
                        'product_uom': ref('product.product_uom_unit'),
                        'product_uom_qty': 1,
                        'location_id': ref('stock.stock_location_stock'),
                        'location_dest_id':
                            ref('stock.stock_location_customers')
                        }
                 ),
                ]
            })
        self.picking.action_confirm()
        self.dispatch = self.picking_dispatch_model.create({
            'move_ids': [
                (4, line.id) for line in self.picking.move_lines
            ]
        })

    def test_related_picking(self):
        picking_ids = [pick.id for pick in self.dispatch.related_picking_ids]
        self.assertEqual(picking_ids, [self.picking.id])
        self.assertEqual(self.picking.state, 'confirmed')
        for move in self.picking.move_lines:
            self.assertEqual(move.state, 'confirmed')

    def test_assign(self):
        self.dispatch.write({'picker_id': self.ref('base.user_demo'),
                             })
        self.dispatch.action_assign()
        self.assertEqual(self.dispatch.state, 'assigned')
        for move in self.picking.move_lines:
            self.assertEqual(move.state, 'confirmed')

    def test_assign_moves(self):
        self.dispatch.check_assign_all()
        for move in self.picking.move_lines:
            self.assertEqual(move.state, 'assigned')
        self.assertEqual(self.picking.state, 'assigned')

    def test_cancel(self):
        self.dispatch.action_cancel()
        self.assertEqual(self.dispatch.state, 'cancel')
        for move in self.picking.move_lines:
            self.assertEqual(move.state, 'cancel')
        self.assertEqual(self.picking.state, 'cancel')

    def test_done(self):
        self.test_assign()
        for move in self.picking.move_lines:
            move.action_done()
        self.assertEqual(self.picking.state, 'done')
        for move in self.picking.move_lines:
            move.refresh()
            self.assertEqual(move.state, 'done')
        self.dispatch.refresh()
        self.assertEqual(self.dispatch.state, 'done')

    def test_related_picking_ids(self):
        # Simple Test to fix issue #148
        dispatch = self.picking_dispatch_model.new({})

        # Just read related_picking_ids was raising ProgrammingError
        self.assertEqual(0, len(dispatch.related_picking_ids))

        # Test with a database record
        db_dispatch = self.picking_dispatch_model.create({
            'name': 'Test picking dispatch'
        })
        self.assertEqual(0, len(db_dispatch.related_picking_ids))

        self.stock_move.write({
            'dispatch_id': db_dispatch.id
        })
        db_dispatch.refresh()
        self.assertEqual(1, len(db_dispatch.related_picking_ids))
