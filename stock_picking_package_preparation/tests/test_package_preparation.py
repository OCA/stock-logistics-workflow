# -*- coding: utf-8 -*-
# Copyright 2015 Guewen Baconnier
# Copyright 2016 Lorenzo Battistini - Agile Business Group
# Copyright 2016 Alessio Gerace - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPackagePreparation(TransactionCase):

    def _create_picking(self):
        src_location = self.env.ref('stock.stock_location_stock')
        dest_location = self.env.ref('stock.stock_location_customers')
        return self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': src_location.id,
            'location_dest_id': dest_location.id,
        })

    def _create_move(self, picking, product, quantity=5.0):
        src_location = self.env.ref('stock.stock_location_stock')
        dest_location = self.env.ref('stock.stock_location_customers')
        return self.env['stock.move'].create({
            'name': '/',
            'picking_id': picking.id,
            'product_id': product.id,
            'product_uom_qty': quantity,
            'product_uom': product.uom_id.id,
            'location_id': src_location.id,
            'location_dest_id': dest_location.id,
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
        packaging_tpl = self.env['product.template'].create({'name': 'Pallet'})
        self.packaging = self.env['product.packaging'].create({
            'name': 'Pallet',
            'product_tmpl_id': packaging_tpl.id,
        })
        self.picking_a = self._create_picking()
        self.move_a_1 = self._create_move(self.picking_a,
                                          self.product1)
        self.move_a_2 = self._create_move(self.picking_a,
                                          self.product2)
        self.picking_b = self._create_picking()
        self.move_b_1 = self._create_move(self.picking_b,
                                          self.product1)

    def test_put_in_pack(self):
        pickings = self.picking_a + self.picking_b
        pickings.action_confirm()
        pickings.force_assign()

        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()
        self.assertTrue(prep.package_id)
        self.assertEquals(
            pickings.mapped('move_lines.linked_move_operation_ids.'
                            'operation_id.result_package_id'),
            prep.package_id,
            "All the moves should have a stock.quant.operation with "
            "the same result package"
        )

    def test_done(self):
        pickings = self.picking_a + self.picking_b
        pickings.action_confirm()
        pickings.force_assign()

        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()

        prep.action_done()

        self.assertTrue(
            all(picking.state == 'done' for picking in pickings)
        )

    def test_pack_values(self):
        pickings = self.picking_a + self.picking_b
        pickings.action_confirm()
        pickings.force_assign()
        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()
        package = prep.package_id
        self.assertEquals(package.packaging_id, self.packaging)

    def test_weight(self):
        location = self.env.ref('stock.stock_location_customers')
        self.product1.weight = 5  # * 5 units
        self.product2.weight = 2  # * 5 units
        pickings = self.picking_a + self.picking_b
        pickings.action_confirm()
        pickings.force_assign()
        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()
        prep.action_done()
        self.assertEquals(prep.weight, 60.0)
        self.assertEquals(
            prep.package_id.location_id, location)
