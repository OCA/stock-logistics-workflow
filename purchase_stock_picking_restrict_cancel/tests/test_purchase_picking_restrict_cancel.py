# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase, Form
from odoo.exceptions import UserError


class TestRestrictCancelStockMove(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref('stock.warehouse0')
        cls.warehouse.write({'reception_steps': 'three_steps'})
        cls.stock_loc = cls.warehouse.lot_stock_id
        cls.input_loc = cls.warehouse.wh_input_stock_loc_id
        cls.qc_loc = cls.warehouse.wh_qc_stock_loc_id
        cls.internal_pt = cls.warehouse.int_type_id
        cls.internal_pt.active = True
        # Create a vendor
        partner = cls.env['res.partner'].create({
            'name': 'Smith'
        })
        # Create product and set the default vendor
        product_form = Form(cls.env['product.product'])
        product_form.name = 'Product A'
        product_form.type = 'product'
        product_form.purchase_ok = True
        with product_form.seller_ids.new() as seller:
            seller.name = partner
        product_form.route_ids.add(
            cls.env.ref('purchase_stock.route_warehouse0_buy'))
        cls.dummy_product = product_form.save()
        # Create product reordering rule
        orderpoint_form = Form(cls.env['stock.warehouse.orderpoint'])
        orderpoint_form.warehouse_id = cls.warehouse
        orderpoint_form.location_id = cls.warehouse.lot_stock_id
        orderpoint_form.product_id = cls.dummy_product
        orderpoint_form.product_min_qty = 0.000
        orderpoint_form.product_max_qty = 10.000
        cls.order_point = orderpoint_form.save()

    def test_restrict(self):
        # Run scheduler, this should create new PO and Stock Move (QC -> Stock)
        self.env['procurement.group'].run_scheduler()
        # Find newly created move from QC -> Stock
        qc_to_stock_move = self.env['stock.move'].search([
            ('product_id', '=', self.dummy_product.id),
            ('location_id', '=', self.qc_loc.id),
            ('location_dest_id', '=', self.stock_loc.id),
        ])
        qc_to_stock_picking = qc_to_stock_move.picking_id
        self.assertNotEqual(qc_to_stock_move.state, 'cancel')
        with self.assertRaises(UserError):
            qc_to_stock_picking.action_cancel()
