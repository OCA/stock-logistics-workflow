# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestStockMove(common.TransactionCase):

    def setUp(self):
        super(TestStockMove, self).setUp()
        # Useful models
        self.Picking = self.env['stock.picking']
        self.product_id_1 = self.env.ref('product.product_product_8')
        self.product_id_2 = self.env.ref('product.product_product_11')
        self.product_id_3 = self.env.ref('product.product_product_6')
        self.picking_type_in = self.env.ref('stock.picking_type_in')
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')
        self.customer_location = self.env.ref('stock.stock_location_customers')

    def _create_picking(self):
        """Create a Picking."""
        picking = self.Picking.create({
            'picking_type_id': self.picking_type_in.id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.customer_location.id,
            'move_lines': [(0, 0,
                            {'name': 'move 1',
                             'product_id': self.product_id_1.id,
                             'product_uom_qty': 5.0,
                             'product_uom': self.product_id_1.uom_id.id,
                             'location_id': self.supplier_location.id,
                             'location_dest_id': self.customer_location.id}),
                           (0, 0,
                            {'name': 'move 2',
                             'product_id': self.product_id_2.id,
                             'product_uom_qty': 5.0,
                             'product_uom': self.product_id_2.uom_id.id,
                             'location_id': self.supplier_location.id,
                             'location_dest_id': self.customer_location.id}),
                           (0, 0,
                            {'name': 'move 3',
                             'product_id': self.product_id_3.id,
                             'product_uom_qty': 5.0,
                             'product_uom': self.product_id_3.uom_id.id,
                             'location_id': self.supplier_location.id,
                             'location_dest_id': self.customer_location.id})]
        })
        return picking

    def test_move_lines_sequence(self):

        self.picking = self._create_picking()
        self.picking._compute_max_line_sequence()
        self.picking.move_lines.write({'product_uom_qty': 10.0})
        self.picking2 = self.picking.copy()
        self.assertEqual(self.picking2[0].move_lines[0].sequence,
                         self.picking.move_lines[0].sequence,
                         'The Sequence is not copied properly')
        self.assertEqual(self.picking2[0].move_lines[1].sequence,
                         self.picking.move_lines[1].sequence,
                         'The Sequence is not copied properly')
        self.assertEqual(self.picking2[0].move_lines[2].sequence,
                         self.picking.move_lines[2].sequence,
                         'The Sequence is not copied properly')
