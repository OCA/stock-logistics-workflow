# Copyright 2025 Akretion France (http://www.akretion.com/)
# @author: Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestLockLocation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_out = cls.env.ref("stock.picking_type_out")
        cls.company_id = cls.env.ref("base.main_company")

    def test_lock_location(self):
        self.assertFalse(self.picking_out.lock_location_id)
        self.company_id.lock_location_id = True
        self.assertTrue(self.picking_out.lock_location_id)
        self.assertFalse(self.picking_out.lock_location_dest_id)

    def test_lock_new_picking_type(self):
        self.company_id.lock_location_id = True
        picking_type = self.env["stock.picking.type"].create(
            {
                "name": "Test Picking Type",
                "code": "internal",
                "sequence_code": "Test",
            }
        )

        self.assertFalse(picking_type.lock_location_id)
        picking_type.code = "incoming"
        self.assertTrue(picking_type.lock_location_id)
