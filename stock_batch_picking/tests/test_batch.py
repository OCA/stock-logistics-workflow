# Copyright 2018 Tecnativa - Carlos Dauden

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestBatchPicking(TransactionCase):

    def setUp(self):
        super(TestBatchPicking, self).setUp()
        self.user_demo = self.env.ref('base.user_demo')

        self.stock_loc = self.browse_ref('stock.stock_location_stock')
        self.customer_loc = self.browse_ref('stock.stock_location_customers')

        self.batch_model = self.env['stock.batch.picking']
        # Delete (in transaction) all batches for simplify tests.
        self.batch_model.search([]).unlink()

        self.picking_model = self.env['stock.picking']

        self.product6 = self.env.ref('product.product_product_6')
        self.product7 = self.env.ref('product.product_product_7')
        self.product9 = self.env.ref('product.product_product_9')
        self.product10 = self.env.ref('product.product_product_10')

        self.picking = self.create_simple_picking([
            self.product6.id,
            self.product7.id,
        ])
        self.picking.action_confirm()

        self.picking2 = self.create_simple_picking([
            self.product9.id,
            self.product10.id,
        ])
        self.picking2.action_confirm()

        self.batch = self.batch_model.create({
            'picker_id': self.env.uid,
            'picking_ids': [
                (4, self.picking.id),
                (4, self.picking2.id),
            ]
        })

    def create_simple_picking(self, product_ids, batch_id=False):
        return self.picking_model.create({
            'picking_type_id': self.ref('stock.picking_type_out'),
            'location_id': self.stock_loc.id,
            'location_dest_id': self.customer_loc.id,
            'batch_picking_id': batch_id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': product_id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'location_id': self.stock_loc.id,
                    'location_dest_id': self.customer_loc.id
                }) for product_id in product_ids
            ]
        })

    def test_assign__no_picking(self):
        batch = self.batch_model.create({})
        with self.assertRaises(UserError):
            batch.action_assign()

        # Even with multiple batches
        batches = batch | self.batch_model.create({})
        with self.assertRaises(UserError):
            batches.action_assign()

    def test_assign(self):
        self.assertEqual('draft', self.batch.state)
        self.assertEqual('confirmed', self.picking.state)
        self.assertEqual('confirmed', self.picking2.state)

        self.assertEqual(0, len(self.batch.move_line_ids))
        self.assertEqual(4, len(self.batch.move_lines))

        self.batch.action_assign()

        self.assertEqual('assigned', self.batch.state)
        self.assertEqual('assigned', self.picking.state)
        self.assertEqual('assigned', self.picking2.state)

        self.assertEqual(4, len(self.batch.move_line_ids))
        self.assertEqual(4, len(self.batch.move_lines))

    def test_assign_with_cancel(self):
        self.picking2.action_cancel()
        self.assertEqual('draft', self.batch.state)
        self.assertEqual('confirmed', self.picking.state)
        self.assertEqual('cancel', self.picking2.state)

        self.batch.action_assign()

        self.assertEqual('assigned', self.batch.state)
        self.assertEqual('assigned', self.picking.state)
        self.assertEqual('cancel', self.picking2.state)

    def test_action_transfer(self):
        self.batch.action_assign()

        self.assertEqual('assigned', self.batch.state)
        self.assertEqual('assigned', self.picking.state)
        self.assertEqual('assigned', self.picking2.state)

        self.assertEqual(4, len(self.batch.move_line_ids))

        self.assertEqual(
            {(0, 1)},
            {(op.qty_done, op.product_qty)
             for op in self.batch.move_line_ids}
        )

        self.batch.action_transfer()

        self.assertEqual('done', self.batch.state)
        self.assertEqual('done', self.picking.state)
        self.assertEqual('done', self.picking2.state)

        self.assertEqual(4, len(self.batch.move_line_ids))

        self.assertEqual(
            {(1, 1)},
            {(op.qty_done, op.product_qty)
             for op in self.batch.move_line_ids}
        )

    def test_action_transfer__unavailable(self):

        picking3 = self.create_simple_picking([
            self.ref('product.product_product_8')
        ])

        self.batch = self.batch_model.create({
            'picker_id': self.env.uid,
            'picking_ids': [
                (4, self.picking.id),
                (4, picking3.id),
            ]
        })

        self.assertEqual('draft', picking3.state)
        self.assertEqual('confirmed', self.picking.state)
        self.batch.action_transfer()
        self.assertEqual('confirmed', picking3.state)
        self.assertEqual('done', self.picking.state)

    def test_cancel(self):
        self.assertEqual('draft', self.batch.state)
        self.assertEqual('confirmed', self.picking.state)
        self.assertEqual('confirmed', self.picking2.state)

        self.batch.action_cancel()

        self.assertEqual('cancel', self.batch.state)
        self.assertEqual('cancel', self.picking.state)
        self.assertEqual('cancel', self.picking2.state)

    def test_cancel_multi(self):
        picking3 = self.create_simple_picking([
            self.ref('product.product_product_8')
        ])

        batch2 = self.batch_model.create({
            'picker_id': self.env.uid,
            'picking_ids': [
                (4, picking3.id),
            ]
        })

        batches = self.batch | batch2

        batches.action_cancel()

        self.assertEqual('cancel', self.batch.state)
        self.assertEqual('cancel', self.picking.state)
        self.assertEqual('cancel', self.picking2.state)

        self.assertEqual('cancel', batch2.state)
        self.assertEqual('cancel', picking3.state)

    def test_cancel__no_pickings(self):
        batch = self.batch_model.create({})
        self.assertEqual('draft', batch.state)
        batch.action_cancel()
        self.assertEqual('cancel', batch.state)

    def test_all_cancel_or_done__on_cancel(self):
        self.picking.do_transfer()
        self.picking2.action_cancel()

        self.assertEqual('done', self.batch.state)

    def test_all_cancel_or_done__on_done(self):
        self.picking2.action_cancel()
        self.picking.do_transfer()

        self.assertEqual('done', self.batch.state)

    def test_stock_picking_copy(self):
        picking = self.batch.picking_ids[0]
        self.assertEqual(self.batch, picking.batch_picking_id)
        copy = picking.copy()
        self.assertFalse(copy.batch_picking_id)

    def test_create_wizard(self):
        wizard = self.env['stock.batch.picking.creator'].create({
            'name': 'Unittest wizard',
        })

        # Pickings already in batch.
        with self.assertRaises(UserError):
            wizard.with_context(active_ids=[self.picking.id])\
                .action_create_batch()

        # Creating and selecting (too) another picking
        picking3 = self.create_simple_picking([
            self.ref('product.product_product_8'),
        ])
        picking3.action_confirm()

        self.assertEqual(0, self.batch_model.search_count(
            [('name', '=', 'Unittest wizard')]
        ))

        wizard.with_context(active_ids=[self.picking.id, picking3.id])\
            .action_create_batch()

        batch = self.batch_model.search(
            [('name', '=', 'Unittest wizard')]
        )
        self.assertEqual(1, len(batch))

        # Only picking3 because self.picking is already in another batch.
        self.assertEqual(picking3, batch.picking_ids)
        self.assertEqual(batch, picking3.batch_picking_id)

    def test_wizard_picker_id(self):
        wh_main = self.browse_ref("stock.warehouse0")

        wizard_model = self.env['stock.batch.picking.creator']
        wizard = wizard_model.create({
            'name': 'Unittest wizard',
        })
        self.assertFalse(wizard.picker_id)

        wh_main.default_picker_id = self.env.user

        wizard = wizard_model.create({
            'name': 'Unittest wizard',
        })
        self.assertEqual(self.env.user, wizard.picker_id)

        other_wh = self.env['stock.warehouse'].create({
            'name': 'Unittest other warehouse',
            'code': 'UWH',
        })

        wizard = wizard_model.with_context(warehouse_id=other_wh.id).create({
            'name': 'Unittest wizard',
        })
        self.assertFalse(wizard.picker_id)

        user2 = self.env['res.users'].create({
            'name': 'Unittest user',
            'login': 'unittest_user'
        })
        other_wh.default_picker_id = user2
        wizard = wizard_model.with_context(warehouse_id=other_wh.id).create({
            'name': 'Unittest wizard',
        })
        self.assertEqual(user2, wizard.picker_id)

    def test_backorder(self):
        # Change move lines quantities for product 6 and 7
        for move in self.batch.move_lines:
            if move.product_id == self.product6:
                move.product_uom_qty = 5
            elif move.product_id == self.product7:
                move.product_uom_qty = 2

        self.batch.action_assign()

        # Mark product 6 as partially processed and 7 and 9 as fully processed.
        for operation in self.batch.move_line_ids:
            if operation.product_id == self.product6:
                operation.qty_done = 3
            elif operation.product_id == self.product7:
                operation.qty_done = 2
            elif operation.product_id == self.product9:
                operation.qty_done = 1

        self.batch.action_transfer()

        self.assertEqual('done', self.picking.state)
        self.assertEqual('done', self.picking2.state)

        # A backorder has been created for product with
        # 5 - 3 = 2 qty to process.
        backorder = self.picking_model.search([
            ('backorder_id', '=', self.picking.id)
        ])
        self.assertEqual(1, len(backorder))

        self.assertEqual('assigned', backorder.state)
        self.assertEqual(1, len(backorder.move_lines))
        self.assertEqual(self.product6, backorder.move_lines[0].product_id)
        self.assertEqual(2, backorder.move_lines[0].product_uom_qty)
        self.assertEqual(1, len(backorder.move_line_ids))
        self.assertEqual(2, backorder.move_line_ids[0].product_qty)
        self.assertEqual(0, backorder.move_line_ids[0].qty_done)

        backorder2 = self.picking_model.search([
            ('backorder_id', '=', self.picking2.id)
        ])
        self.assertEqual(1, len(backorder2))

        self.assertEqual('assigned', backorder2.state)
        self.assertEqual(1, len(backorder2.move_lines))
        self.assertEqual(self.product10, backorder2.move_lines.product_id)
        self.assertEqual(1, backorder2.move_lines.product_uom_qty)
        self.assertEqual(1, len(backorder2.move_line_ids))
        self.assertEqual(1, backorder2.move_line_ids.product_qty)
        self.assertEqual(0, backorder2.move_line_ids.qty_done)

    def test_assign_draft_pick(self):
        picking3 = self.create_simple_picking([
            self.ref('product.product_product_11'),
        ], batch_id=self.batch.id)
        self.assertEqual('draft', picking3.state)

        self.batch.action_transfer()
        self.assertEqual('done', self.batch.state)
        self.assertEqual('done', self.picking.state)
        self.assertEqual('done', self.picking2.state)
        self.assertEqual('done', picking3.state)

    def test_package(self):

        warehouse = self.browse_ref('stock.warehouse0')
        warehouse.delivery_steps = 'pick_ship'

        group = self.env['procurement.group'].create({
            'name': 'Test',
            'move_type': 'direct',
        })

        procurement = self.env['procurement.order'].create({
            'name': 'test',
            'group_id': group.id,
            'warehouse_id': warehouse.id,
            'product_id': self.ref('product.product_product_11'),
            'product_uom_qty': 1,
            'product_uom': self.ref('product.product_uom_unit'),
            'location_id': self.customer_loc.id,
        })
        procurement.run()

        pickings = self.picking_model.search([
            ('group_id', '=', group.id)
        ])
        self.assertEqual(2, len(pickings))
        picking = pickings.filtered(lambda p: p.state == 'confirmed')
        picking.action_assign()

        picking.move_line_ids[0].qty_done = 1
        package_id = picking.put_in_pack()
        picking.do_transfer()

        package = self.env['stock.quant.package'].browse(package_id)

        other_picking = pickings.filtered(lambda p: p.id != picking.id)
        self.assertEqual('assigned', other_picking.state)
        self.assertEqual(
            package, other_picking.move_line_ids.package_id,
        )

        # We add the 'package' picking in batch
        other_picking.batch_picking_id = self.batch

        self.batch.action_assign()

        self.batch.action_transfer()
        self.assertEqual('done', self.batch.state)
        self.assertEqual('done', self.picking.state)
        self.assertEqual('done', self.picking2.state)
        self.assertEqual('done', other_picking.state)

        self.assertEqual(self.customer_loc, package.location_id)

    def test_remove_undone(self):
        self.picking2.action_cancel()

        picking3 = self.create_simple_picking([
            self.ref('product.product_product_11')
        ], batch_id=self.batch.id)
        picking3.do_transfer()

        picking4 = self.create_simple_picking([
            self.ref('product.product_product_11')
        ], batch_id=self.batch.id)

        self.assertEqual('confirmed', self.picking.state)
        self.assertEqual('cancel', self.picking2.state)
        self.assertEqual('done', picking3.state)
        self.assertEqual('draft', picking4.state)

        self.assertEqual('draft', self.batch.state)

        self.batch.remove_undone_pickings()

        self.assertEqual('done', self.batch.state)
        self.assertEqual(2, len(self.batch.picking_ids))

        self.assertEqual(self.picking2 | picking3, self.batch.picking_ids)

    def test_partial_done(self):
        # If user filled some qty_done manually in operations tab,
        # we want only these qties to be processed.
        # So picking with no qties processed are release and backorder are
        # created for picking partially processed.

        self.batch.action_assign()
        self.assertEqual('assigned', self.picking.state)
        self.assertEqual('assigned', self.picking2.state)

        self.picking.move_line_ids[0].qty_done = 1

        self.batch.action_transfer()

        self.assertEqual(self.picking, self.batch.picking_ids)
        self.assertEqual('done', self.picking.state)
        # Second picking is released (and still confirmed)
        self.assertEqual('assigned', self.picking2.state)
        self.assertFalse(self.picking2.batch_picking_id)

        picking_backorder = self.picking_model.search([
            ('backorder_id', '=', self.picking.id)
        ])
        self.assertEqual(1, len(picking_backorder.move_lines))
