# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.tests.common import TransactionCase


class TestStockPickingOriginReference(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Models
        cls.picking_model = cls.env["stock.picking"]

        # Existing Instances
        cls.picking_type_in_id = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out_id = cls.env.ref("stock.picking_type_out")
        cls.location_suppliers = cls.env.ref("stock.stock_location_suppliers")
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.location_customers = cls.env.ref("stock.stock_location_customers")

        # TO BE USED IN CHILDREN TESTS
        cls.partner_model = cls.env["res.partner"]

        cls.product = cls.env.ref("product.product_product_3")

        cls.partner = cls.partner_model.create({"name": "Test Partner"})

    def _create_picking(
        self, picking_type_id, location_id, location_dest_id, origin=False
    ):
        picking = self.picking_model.create(
            {
                "picking_type_id": picking_type_id.id,
                "location_id": location_id.id,
                "location_dest_id": location_dest_id.id,
                "scheduled_date": fields.Date.today(),
                "priority": "1",
                "origin": origin,
            }
        )
        return picking

    def test_01_check_correct_value(self):
        """
        Check that the OUT transfer references to the IN transfer with the `origin
        reference` field.
        """
        self.picking_in = self._create_picking(
            self.picking_type_in_id, self.location_suppliers, self.location_stock
        )
        self.picking_out = self._create_picking(
            self.picking_type_out_id,
            self.location_stock,
            self.location_customers,
            origin=self.picking_in.name,
        )
        self.assertEqual(self.picking_out.origin, self.picking_in.name)
        self.assertEqual(
            self.picking_out.origin_reference,
            self.picking_in,
            "The " "Origin Reference should point to the IN transfer.",
        )
