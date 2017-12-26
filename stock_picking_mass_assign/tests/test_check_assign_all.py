# © 2017 JARSA Sistemas S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import common
from odoo.tools.translate import _


class TestCheckAssignAll(common.TransactionCase):

    def setUp(self):
        super(TestCheckAssignAll, self).setUp()
        self.picking_type_out = self.env.ref('stock.picking_type_out')
        self.product = self.env.ref('product.product_product_11')
        self.product_uom_unit = self.env.ref('product.product_uom_unit')
        self.location_components = self.env.ref(
            'stock.stock_location_components')
        self.stock_location_output = self.env.ref(
            'stock.stock_location_output')
        self.check_assign_all_wiz = self.env['stock.picking.check.assign.all']
        self.picking_obj = self.env['stock.picking']

    def create_stock_picking(self):
        picking = self.picking_obj.create({
            'name': self.picking_type_out.sequence_id.next_by_id(),
            'picking_type_id': self.picking_type_out.id,
            'location_id': self.location_components.id,
            'location_dest_id': self.stock_location_output.id,
            'move_lines': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 10,
                'product_uom': self.product_uom_unit.id,
                'location_id': self.location_components.id,
                'location_dest_id': self.stock_location_output.id,
                'date': '2013-12-20',
                'date_expected': '2013-12-20',
                'procure_method': 'make_to_stock',
            })],
        })
        picking.action_confirm()
        return picking

    def test_10_check_assign_partially_available(self):
        pickings = self.create_stock_picking()
        pickings |= self.create_stock_picking()
        pickings |= self.create_stock_picking()
        self.check_assign_all_wiz.with_context(
            active_ids=pickings.ids, process_picking=True).create({}).check()
        self.assertEquals(
            pickings.mapped('state'),
            ['done', 'done', 'assigned'])
        return True

    def test_20_check_assign_no_orders(self):
        pickings = self.create_stock_picking()
        pickings |= self.create_stock_picking()
        pickings |= self.create_stock_picking()
        with self.assertRaisesRegexp(
                ValidationError, _('No selected delivery orders')):
            self.check_assign_all_wiz.with_context().create({}).check()
        return True

    def test_30_check_all(self):
        pickings = self.create_stock_picking()
        pickings |= self.create_stock_picking()
        pickings |= self.create_stock_picking()
        res = self.picking_obj.check_assign_all()
        self.assertEqual(res, True)
        return True
