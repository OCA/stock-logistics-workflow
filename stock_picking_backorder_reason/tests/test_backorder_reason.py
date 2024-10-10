# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from .common import TestPickingBackorder


class TestPickingBackorder(TestPickingBackorder, TransactionCase):
    def test_picking_type_constraint(self):
        msg = (
            "If you enable the backorder reason feature, you should choose "
            "if this is for sale or purchase"
        )
        with self.assertRaises(ValidationError, msg=msg):
            self.picking_type_in.backorder_reason_purchase = False
        with self.assertRaises(ValidationError, msg=msg):
            self.picking_type_out.backorder_reason_sale = False
        # Try to deactivate the reason flow
        self.picking_type_out.backorder_reason = False

    def test_company_defaults(self):
        # Default behavior for sales
        partner = self.partner_model.create({"name": "Test Sale Create"})
        self.assertEqual("create", partner.sale_reason_backorder_strategy)
        # Change to cancel for sale flows
        self.env.company.partner_sale_backorder_default_strategy = "cancel"
        partner = self.partner_model.create({"name": "Test Sale Cancel"})
        self.assertEqual("cancel", partner.sale_reason_backorder_strategy)

        # Default behavior for purchase
        partner = self.partner_model.create({"name": "Test Purchase Create"})
        self.assertEqual("create", partner.purchase_reason_backorder_strategy)
        # Change to cancel for purchase flows
        self.env.company.partner_purchase_backorder_default_strategy = "cancel"
        partner = self.partner_model.create({"name": "Test Cancel"})
        self.assertEqual("cancel", partner.purchase_reason_backorder_strategy)

    def test_no_backorder(self):
        """
        Create a stock picking
        Validate the whole lines
        Try to validate the picking.
        The result should be True (and not the backorder wizard)
        """

        self.picking = self.stock_picking_model.create(
            {
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "partner_id": self.partner.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "a move",
                            "product_id": self.product.id,
                            "product_uom_qty": 10,
                            "product_uom": self.product.uom_id.id,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.stock_location.id,
                        },
                    )
                ],
            }
        )

        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking.move_line_ids.write({"qty_done": 10.0})

        result = self.picking.button_validate()
        self.assertTrue(isinstance(result, bool) and result)
