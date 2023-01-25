# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from odoo.addons.stock_picking_backorder_reason.tests.common import TestPickingBackorder


class TestSalePickingBackorder(TestPickingBackorder, TransactionCase):

    _flow = "purchase"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._create_picking()

        # Add a GRN for our picking
        cls.grn_model = cls.env["stock.grn"]
        cls.grn = cls.grn_model.create(
            {
                "carrier_id": cls.partner.id,
                "delivery_note_supplier_number": "TEST REASON",
                "picking_ids": [
                    (4, cls.picking.id),
                ],
            }
        )
        # Set on reason to keep GRN
        cls.backorder_reason.keep_grn = True

    def _check_backorder_behavior(self):
        res = super()._check_backorder_behavior()
        if self.backorder_action == "create":
            if self.backorder_reason.keep_grn:
                self.assertTrue(self.backorder.grn_id)
                self.assertEqual(self.backorder.grn_id, self.picking.grn_id)
            else:
                self.assertFalse(self.backorder.grn_id)
        return res

    def test_backorder_reason_grn(self):
        self.backorder_action = "create"
        self.purchase_backorder = "create"
        self._check_backorder_behavior()

    def test_backorder_reason_no_grn(self):
        self.backorder_reason.keep_grn = False
        self.backorder_action = "create"
        self.purchase_backorder = "create"
        self._check_backorder_behavior()
