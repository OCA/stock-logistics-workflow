# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProductSupplierinfoForCustomerPicking(TransactionCase):

    def setUp(self):
        super(TestProductSupplierinfoForCustomerPicking, self).setUp()
        self.computer_SC234 = self.browse_ref("product.product_product_3")
        self.agrolait = self.browse_ref("base.res_partner_2")
        self.computer_SC234.write({
            'customer_ids': [(0, 0, {
                'name': self.agrolait.id,
                'product_code': 'test_agrolait',
                'type': 'customer',
            })],
        })

    def test_product_supplierinfo_for_customer_picking(self):
        delivery_picking = self.env['stock.picking'].new({
            'partner_id': self.agrolait.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
        })
        delivery_picking.onchange_picking_type()
        delivery_picking = self.env['stock.picking'].create({
            'partner_id': delivery_picking.partner_id.id,
            'picking_type_id': delivery_picking.picking_type_id.id,
            'location_id': delivery_picking.location_id.id,
            'location_dest_id': delivery_picking.location_dest_id.id,
            'move_lines': [(0, 0, {
                'name': self.computer_SC234.partner_ref,
                'product_id': self.computer_SC234.id,
                'product_uom': self.computer_SC234.uom_id.id,
                'product_uom_qty': 1.0,
            })]
        })
        move = delivery_picking.move_lines[0]
        move._compute_product_customer_code()
        self.assertEqual(move.product_customer_code, 'test_agrolait')
