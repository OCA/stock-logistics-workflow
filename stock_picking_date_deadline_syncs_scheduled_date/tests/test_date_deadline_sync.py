# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase


class TestDateDeadlineSync(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "product"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        stock_location_id = cls.env.ref("stock.stock_location_stock").id
        stock_location_customers_id = cls.env.ref("stock.stock_location_customers").id
        stock_location_suppliers_id = cls.env.ref("stock.stock_location_suppliers").id
        cls.out_picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": stock_location_id,
                "location_dest_id": stock_location_customers_id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test line",
                            "product_id": cls.product.id,
                            "product_uom_qty": 1.0,
                            "product_uom": cls.product.uom_id.id,
                            "location_id": stock_location_id,
                            "location_dest_id": stock_location_customers_id,
                        },
                    )
                ],
            }
        )
        cls.in_picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": stock_location_suppliers_id,
                "location_dest_id": stock_location_id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test line",
                            "product_id": cls.product.id,
                            "product_uom_qty": 1.0,
                            "product_uom": cls.product.uom_id.id,
                            "location_id": stock_location_suppliers_id,
                            "location_dest_id": stock_location_id,
                        },
                    )
                ],
            }
        )

    def _test_deadline_changes(self, picking):
        init_deadline = datetime.now() + timedelta(days=5)
        move = picking.move_ids
        move.date_deadline = init_deadline
        move.date = init_deadline
        picking.action_assign()
        # Change Delivery Date on Sale Order > Change Scheduled and Deadline dates
        self.assertEqual(picking.date_deadline, init_deadline)
        self.assertEqual(move.date_deadline, init_deadline)
        self.assertEqual(picking.scheduled_date, init_deadline)
        self.assertEqual(move.date, init_deadline)
        # Change Scheduled on picking > no change on Date Deadline
        re_scheduled_date = init_deadline + timedelta(days=10)
        picking.scheduled_date = re_scheduled_date
        self.assertEqual(picking.date_deadline, init_deadline)
        self.assertEqual(move.date_deadline, init_deadline)
        self.assertEqual(picking.scheduled_date, re_scheduled_date)
        self.assertEqual(move.date, re_scheduled_date)
        # Change Delivery Date on Sale Order > Change Scheduled and Deadline dates
        final_deadline = init_deadline + timedelta(days=15)
        move.date_deadline = final_deadline
        self.assertEqual(picking.date_deadline, final_deadline)
        self.assertEqual(move.date_deadline, final_deadline)
        self.assertEqual(picking.scheduled_date, final_deadline)
        self.assertEqual(move.date, final_deadline)

    def test_outgoing_date_sync(self):
        """Test Outgoing shipments deadline date syncs scheduled date"""
        self._test_deadline_changes(self.out_picking)

    def test_incoming_date_sync(self):
        """Test Incoming shipments deadline date syncs scheduled date"""
        self._test_deadline_changes(self.in_picking)
