from openerp.tests import TransactionCase


class TestPickingDispatch(TransactionCase):

    def setUp(self):
        super(TestPickingDispatch, self).setUp()
        self.picking_dispatch_model = self.env['picking.dispatch']

        self.stock_move = self.env.ref('stock.incomming_shipment_icecream')

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
