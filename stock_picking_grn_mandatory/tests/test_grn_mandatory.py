# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestStockGrnMandatory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.receipt_type = cls.env.ref("stock.picking_type_in")
        cls.receipt_type.is_grn_mandatory = True
        cls.grn_model = cls.env["stock.grn"]
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Incoming Carrier",
                "email": "my@company.com",
                "company_id": False,
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
                "name": "test_grn_1",
                "location_id": cls.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": cls.env.ref("stock.stock_location_stock").id,
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 1.0,
                "picking_type_id": cls.receipt_type.id,
            }
        )

    def test_grn_mandatory(self):
        """
        Confirm the move, then the picking.
        An error should be raised
        Then, fill in the GRN
        Further validation should pass
        """
        msg = "The picking must be linked to a Goods Received Note"
        self.move._action_confirm()
        with self.assertRaises(UserError, msg=msg):
            self.move.picking_id.button_validate()

        # Fill in the GRN
        delivery_note_supplier_number = "DN TEST"
        grn = self.grn_model.create(
            {
                "carrier_id": self.partner.id,
                "delivery_note_supplier_number": delivery_note_supplier_number,
            }
        )
        self.move.picking_id.grn_id = grn

        # The validation should pass
        self.move.picking_id.button_validate()

    def test_grn_not_mandatory(self):
        """
        Set the picking type as no GRN mandatory
        Confirm the move, then the picking.
        Validation should pass
        """
        self.receipt_type.is_grn_mandatory = False
        self.move._action_confirm()
        self.move.picking_id.button_validate()

    def test_grn_not_mandatory_context(self):
        """
        Pass the bypass value to context
        Confirm the move, then the picking.
        Validation should pass
        """
        self.move._action_confirm()
        self.move.picking_id.with_context(
            __no_pick_receive_note_check=True
        ).button_validate()
