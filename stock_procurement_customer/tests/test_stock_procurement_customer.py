# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestProcurementCustomer(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        # The partner from the picking (core)
        cls.partner_picking = cls.env["res.partner"].create(
            {
                "name": "Test Partner picking",
            }
        )
        cls.procurement = cls.env["procurement.group"].create(
            {
                "name": "Customer Procurement",
                "customer_id": cls.partner.id,
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "type": "product",
            }
        )

        cls.move = cls.env["stock.move"].create(
            {
                "name": cls.product.display_name,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "product_id": cls.product.id,
                "product_uom_qty": 1.0,
                "group_id": cls.procurement.id,
                "partner_id": cls.partner_picking.id,
            }
        )

    def test_procurement(self):
        """
        Create a move with a procurement group containing the customer
        value.
        Check if the created picking has it too
        """
        self.move._action_confirm()
        self.assertTrue(self.move.picking_id)
        self.assertEqual(self.move.picking_id.customer_id, self.partner)

        self.assertNotEqual(
            self.move.picking_id.partner_id,
            self.move.picking_id.customer_id,
        )
        self.assertTrue(self.move.picking_id.customer_id_visible)
