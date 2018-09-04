# Copyright 2015 Guewen Baconnier
# Copyright 2016 Lorenzo Battistini - Agile Business Group
# Copyright 2016 Alessio Gerace - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPackagePreparation(TransactionCase):

    def _create_picking(self):
        return self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.stock_location.id,
            'location_dest_id': self.cust_location.id,
        })

    def _create_move(self, picking, product, quantity=5.0):
        return self.env['stock.move'].create({
            'name': '/',
            'picking_id': picking.id,
            'product_id': product.id,
            'product_uom_qty': quantity,
            'product_uom': product.uom_id.id,
            'location_id': self.stock_location.id,
            'location_dest_id': self.cust_location.id,
        })

    def _create_preparation(self, pickings):
        return self.env['stock.picking.package.preparation'].create({
            'partner_id': self.partner.id,
            'picking_ids': [(6, 0, pickings.ids)],
            'packaging_id': self.packaging.id,
        })

    def setUp(self):
        super(TestPackagePreparation, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        self.product1 = self.env.ref('product.product_product_16')
        self.product2 = self.env.ref('product.product_product_17')
        self.product3 = self.env.ref('product.product_product_20')
        packaging_prod = self.env['product.product'].create({'name': 'Pallet'})
        self.packaging = self.env['product.packaging'].create({
            'name': 'Pallet',
            'product_id': packaging_prod.id,
        })
        self.stock_location = self.env.ref('stock.stock_location_stock')
        self.cust_location = self.env.ref('stock.stock_location_customers')

        self.env['stock.quant']._update_available_quantity(
            self.product1, self.stock_location, 10.0)
        self.env['stock.quant']._update_available_quantity(
            self.product2, self.stock_location, 5.0)

        self.picking_a = self._create_picking()
        self._create_move(self.picking_a, self.product1, 5.0)
        self._create_move(self.picking_a, self.product2, 5.0)

        self.picking_b = self._create_picking()
        self._create_move(self.picking_b, self.product1, 5.0)

    def test_put_in_pack(self):
        pickings = self.picking_a + self.picking_b
        pickings.action_assign()

        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()
        self.assertTrue(prep.package_id)
        self.assertEqual(
            pickings.mapped('move_line_ids.result_package_id'),
            prep.package_id,
            "All the moves should have a stock.quant.operation with "
            "the same result package"
        )

    def test_put_in_pack_keep_done_qty(self):
        pickings = self.picking_a + self.picking_b
        move_lines = pickings.mapped('move_line_ids')

        move_lines.write({'qty_done': 1})
        pickings.action_assign()

        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()
        for move in move_lines:
            self.assertEqual(move.qty_done, 1)

    def test_done(self):
        pickings = self.picking_a + self.picking_b
        pickings.action_assign()

        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()

        prep.action_done()

        self.assertTrue(
            all(picking.state == 'done' for picking in pickings)
        )

    def test_pack_values(self):
        pickings = self.picking_a + self.picking_b
        pickings.action_assign()
        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()
        package = prep.package_id
        self.assertEqual(package.packaging_id, self.packaging)

    def test_weight(self):
        location = self.env.ref('stock.stock_location_customers')
        self.product1.weight = 5  # * 5 units
        self.product2.weight = 2  # * 5 units
        pickings = self.picking_a + self.picking_b
        pickings.action_assign()
        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()
        prep.action_done()
        self.assertEqual(prep.weight, 60.0)
        self.assertEqual(
            prep.package_id.location_id, location)

    def test_cancel_draft(self):
        pickings = self.picking_a + self.picking_b
        pickings.action_assign()

        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()
        prep.action_cancel()

        self.assertTrue(
            all(p.state == 'cancel' for p in prep))
        self.assertTrue(
            all(not p.package_id for p in prep))

        prep.action_draft()
        prep.action_put_in_pack()
        prep.action_done()

        with self.assertRaises(UserError):
            prep.action_cancel()
