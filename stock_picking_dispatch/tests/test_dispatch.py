# -*- coding: utf-8 -*-

from datetime import date, timedelta

from openerp.exceptions import UserError, ValidationError
from openerp.tests.common import TransactionCase


class TestPickingDispatch(TransactionCase):

    def setUp(self):
        super(TestPickingDispatch, self).setUp()
        self.user_demo = self.env.ref('base.user_demo')

        self.dispatch_model = self.env['picking.dispatch']
        self.picking_model = self.env['stock.picking']

        self.picking = self.create_simple_picking([
            self.ref('product.product_product_6'),
            self.ref('product.product_product_7')
        ])
        self.picking.action_confirm()

        self.dispatch = self.dispatch_model.create({
            'picker_id': self.env.user.id,
            'move_ids': [
                (4, line.id) for line in self.picking.move_lines
            ]
        })

    def create_simple_picking(self, product_ids):
        stock_loc = self.ref('stock.stock_location_stock')
        customer_loc = self.ref('stock.stock_location_customers')

        return self.env['stock.picking'].create({
            'picking_type_id': self.ref('stock.picking_type_out'),
            'location_id': stock_loc,
            'location_dest_id': customer_loc,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': product_id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'location_id': stock_loc,
                    'location_dest_id': customer_loc
                }) for product_id in product_ids
            ]
        })

    def test_picking_search_related_dispatch(self):
        pickings = self.picking_model.search([
            ('related_dispatch_ids', '=', self.dispatch.name)
        ])

        self.assertEqual(pickings, self.picking)

    def test_picking_related_dispatch(self):
        # Coverage test
        empty_picking = self.picking_model.new()
        self.assertFalse(empty_picking.related_dispatch_ids)

        self.assertEqual(self.dispatch, self.picking.related_dispatch_ids)

    def test_constraint(self):
        with self.assertRaises(ValidationError):
            self.dispatch_model.create({'state': 'assigned'})
        self.dispatch_model.create({
            'picker_id': self.env.user.id, 'state': 'assigned'
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

    def test_start(self):
        self.dispatch.action_assign()
        self.assertEqual(self.dispatch.state, 'assigned')

        self.dispatch.date = date.today() + timedelta(days=1)
        with self.assertRaises(UserError):
            self.dispatch.action_progress()

        self.dispatch.date = date.today()
        self.dispatch.action_progress()
        self.assertEqual(self.dispatch.state, 'progress')

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

    def test_cancel__no_move(self):
        dispatch = self.dispatch_model.create({})
        self.assertEqual('draft', dispatch.state)
        dispatch.action_cancel()
        self.assertEqual('cancel', dispatch.state)

    def test_move_done(self):
        self.test_assign()
        for move in self.picking.move_lines:
            move.action_done()
        self.assertEqual(self.picking.state, 'done')
        for move in self.picking.move_lines:
            move.refresh()
            self.assertEqual(move.state, 'done')
        self.dispatch.refresh()
        self.assertEqual(self.dispatch.state, 'done')

    def test_done(self):
        self.test_assign()
        self.dispatch.action_done()
        for move in self.picking.move_lines:
            move.refresh()
            self.assertEqual(move.state, 'done')
        self.dispatch.refresh()
        self.assertEqual(self.dispatch.state, 'done')

    def test_stock_move_copy(self):
        move = self.dispatch.move_ids[0]
        self.assertEqual(self.dispatch, move.dispatch_id)
        copy = move.copy()
        self.assertFalse(copy.dispatch_id)

    def test_check_assign_all(self):
        # Test this method like cron, call with empty recordeset
        self.dispatch_model.check_assign_all()

        for move in self.picking.move_lines:
            self.assertEqual(move.state, 'assigned')
        self.assertEqual(self.picking.state, 'assigned')

    def test_create_wizard(self):
        self.env.user.company_id.default_picker_id = self.user_demo

        wizard = self.env['picking.dispatch.creator'].create({
            'name': 'Unittest wizard',
        })
        self.assertEqual(self.user_demo, wizard.picker_id)

        # Already dispatched picking
        with self.assertRaises(UserError):
            wizard.with_context(active_ids=[self.picking.id])\
                .action_create_dispatch()

        # Creating and selecting (too) another picking
        picking2 = self.create_simple_picking([
            self.ref('product.product_product_8'),
            self.ref('product.product_product_9'),
            self.ref('product.product_product_10'),
        ])
        # One move is canceled
        picking2.move_lines[2].state = 'cancel'
        picking2.action_confirm()

        self.assertEqual(0, self.dispatch_model.search_count(
            [('name', '=', 'Unittest wizard')]
        ))

        wizard.with_context(active_ids=[self.picking.id, picking2.id])\
            .action_create_dispatch()

        dispatch = self.dispatch_model.search(
            [('name', '=', 'Unittest wizard')]
        )
        self.assertEqual(1, len(dispatch))

        self.assertEqual(self.user_demo, dispatch.picker_id)
        # Only picking2 because self.picking moves already dispatched
        self.assertEqual(picking2, dispatch.related_picking_ids)
        self.assertEqual(dispatch, picking2.related_dispatch_ids)

        self.assertEqual(dispatch, picking2.move_lines[0].dispatch_id)
        self.assertEqual(dispatch, picking2.move_lines[1].dispatch_id)
        self.assertFalse(picking2.move_lines[2].dispatch_id)

    def test_create_wizard__wrong_states_only(self):
        wizard = self.env['picking.dispatch.creator'].create({
            'name': 'Unittest wizard',
            'picker_id': self.env.user.id
        })
        picking2 = self.create_simple_picking([
            self.ref('product.product_product_8'),
            self.ref('product.product_product_9'),
        ])
        picking2.move_lines[0].state = 'done'
        picking2.move_lines[1].state = 'cancel'
        picking2.action_confirm()

        with self.assertRaises(UserError):
            wizard.with_context(active_ids=[self.picking.id, picking2.id]) \
                .action_create_dispatch()

        self.assertEqual(0, self.dispatch_model.search_count(
            [('name', '=', 'Unittest wizard')]
        ))

    def test_start_wizard(self):
        dispatch2 = self.dispatch_model.create({
            'picker_id': self.env.user.id,
            'state': 'assigned'
        })

        dispatch3 = self.dispatch_model.create({
            'picker_id': self.env.user.id,
            'state': 'assigned',
            'date': date.today() + timedelta(days=2)
        })

        wizard = self.env['picking.dispatch.start'].with_context(
            active_ids=[self.dispatch.id, dispatch2.id, dispatch3.id]
        ).create({})
        self.assertEqual("<ul><li>1 dispatch(es) will be started</li>"
                         "<li>2 dispatch(es) ignored because current state "
                         "is not 'Assigned' or date is not reached</li></ul>",
                         wizard.message)

        wizard.start()
        self.assertEqual('draft', self.dispatch.state)
        self.assertEqual('progress', dispatch2.state)

    def test_assign_all_wizard(self):
        wizard_model = self.env['picking.dispatch.check.assign.all']

        # No active_ids
        wizard = wizard_model.create({})
        with self.assertRaises(UserError):
            wizard.check()

        wizard = wizard_model.with_context(
            active_ids=[self.dispatch.id]
        ).create({})

        wizard.check()

        for move in self.picking.move_lines:
            self.assertEqual(move.state, 'assigned')
        self.assertEqual(self.picking.state, 'assigned')

    def test_dispatch_assign_picker_wizard(self):
        wizard_model = self.env['picking.dispatch.assign.picker']
        self.dispatch.picker_id = False

        wizard = wizard_model.create({'picker_id': self.user_demo.id})
        with self.assertRaises(UserError):
            wizard.assign_picker()

        self.assertFalse(self.dispatch.picker_id)
        self.assertEqual('draft', self.dispatch.state)
        wizard = wizard_model.with_context(
            active_ids=[self.dispatch.id]
        ).create({'picker_id': self.user_demo.id})

        wizard.assign_picker()
        self.assertEqual(self.user_demo, self.dispatch.picker_id)
        self.assertEqual('assigned', self.dispatch.state)

        # No draft dispatches to assign anymore.
        with self.assertRaises(UserError):
            wizard.assign_picker()
