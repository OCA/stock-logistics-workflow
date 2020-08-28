# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo.tests import common, Form, tagged


@tagged('post_install', '-at_install')
class TestStockPickingLateActivity(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestStockPickingLateActivity, cls).setUpClass()
        cls.user_demo = cls.env.ref("base.demo_user0")
        cls.partner = cls.env['res.partner'].create({
            "name": "Partner test",
        })
        cls.product = cls.env['product.product'].create({
            "name": "Product test 1",
            "type": "product",
        })
        cls.sequence = cls.env['ir.sequence'].create({
            'name': 'test seq',
            'implementation': 'standard',
            'padding': 1,
            'number_increment': 1,
        })
        cls.picking_type = cls.env['stock.picking.type'].create({
            'name': 'Picking type test',
            'code': 'incoming',
            'sequence_id': cls.sequence.id,
            "create_late_picking_activity": True,
            "late_picking_activity_user_id": cls.user_demo.id,
        })
        # Create and validate a picking with 'scheduled_date' == '3 days ago'.
        scheduled_date = datetime.now() - timedelta(days=3)
        cls.picking_1 = cls.create_picking(
            cls.partner, cls.picking_type, cls.product, scheduled_date)
        cls.picking_1.action_confirm()
        product_qty = cls.picking_1.move_lines.product_uom_qty
        cls.picking_1.move_lines.quantity_done = product_qty
        cls.picking_1.button_validate()
        # Create three more pickings. One of them with 'scheduled_date' before
        # current datetime
        scheduled_date = datetime.now() - timedelta(days=2)
        cls.picking_2 = cls.create_picking(
            cls.partner, cls.picking_type, cls.product, scheduled_date)
        cls.picking_2.action_confirm()
        scheduled_date = datetime.now() + timedelta(days=2)
        cls.picking_3 = cls.create_picking(
            cls.partner, cls.picking_type, cls.product, scheduled_date)
        cls.picking_3.action_confirm()

    @classmethod
    def create_picking(cls, partner, picking_type, product, scheduled_date):
        picking_form = Form(
            recordp=cls.env["stock.picking"].with_context(
                default_picking_type_id=picking_type.id),
            view="stock.view_picking_form",
        )
        picking_form.company_id = cls.env.user.company_id
        picking_form.partner_id = partner
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = product
            move.product_uom_qty = 10
        picking = picking_form.save()
        # Edit again to set scheduled_date. scheduled_date is readonly in
        # creation form
        picking_form = Form(picking)
        picking_form.scheduled_date = scheduled_date
        return picking_form.save()

    def test_cron_activity_for_late_picking(self):
        self.env["stock.picking"]._cron_late_picking_activity()
        # Check no activity for self.picking_1
        self.assertFalse(self.picking_1.activity_ids)
        # Check no activity for self.picking_3
        self.assertFalse(self.picking_3.activity_ids)
        # Check: there is an activity for self.picking_2
        self.assertEqual(len(self.picking_2.activity_ids), 1)
        self.assertEqual(
            self.picking_2.activity_ids.activity_type_id,
            self.env.ref("stock_picking_late_activity"
                         ".mail_activity_type_update_scheduled_date"),
        )
        self.assertEqual(self.picking_2.activity_ids.user_id, self.user_demo)
        # Run the cron method again. No other activity should be generated.
        self.env["stock.picking"]._cron_late_picking_activity()
        self.assertEqual(len(self.picking_2.activity_ids), 1)
