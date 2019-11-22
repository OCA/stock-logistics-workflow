# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp.tests.common import TransactionCase


class BatchPickingCommon(TransactionCase):

    def setUp(self):
        super(BatchPickingCommon, self).setUp()
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
