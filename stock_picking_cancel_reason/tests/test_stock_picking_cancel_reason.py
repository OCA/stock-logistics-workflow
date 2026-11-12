# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestStockPickingCancelReason(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        StockPicking = cls.env["stock.picking"]
        CancelReason = cls.env["stock.picking.cancel.reason"]
        partner = cls.env["res.partner"].create({"name": "Test Partner"})
        picking_type_out = cls.env.ref("stock.picking_type_out")
        stock_location = cls.env.ref("stock.stock_location_stock")
        customer_location = cls.env.ref("stock.stock_location_customers")
        cls.reason = CancelReason.create({"name": "Canceled for tests"})
        cls.product = cls.env["product.product"].create({"name": "Product"})
        # create a picking out
        cls.stock_picking = StockPicking.create(
            {
                "partner_id": partner.id,
                "picking_type_id": picking_type_out.id,
                "location_id": stock_location.id,
                "location_dest_id": customer_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 10,
                            "product_uom": cls.product.uom_id.id,
                            "location_id": stock_location.id,
                            "location_dest_id": customer_location.id,
                        }
                    )
                ],
            }
        )

    def test_stock_picking_cancel_reason(self):
        """
        - Cancel a stock picking with the wizard asking for the reason
        - Then the stock picking should be canceled and the reason stored
        """
        StockPickingCancel = self.env["stock.picking.cancel"]
        context = {
            "active_model": "stock.picking",
            "active_ids": [self.stock_picking.id],
        }
        with Form(StockPickingCancel.with_context(**context)) as wizard_form:
            wizard_form.reason_id = self.reason
            wizard_form.description = "Customer requested cancellation"
        wizard = wizard_form.save()
        self.assertEqual(
            wizard.confirm_cancel(), {"type": "ir.actions.act_window_close"}
        )
        self.assertEqual(
            self.stock_picking.state, "cancel", "the stock picking should be canceled"
        )
        self.assertEqual(self.stock_picking.cancel_reason_id.id, self.reason.id)
        self.assertEqual(
            self.stock_picking.cancel_description, "Customer requested cancellation"
        )
        self.assertEqual(self.stock_picking.move_ids.state, "cancel")

    def test_cancel_without_description(self):
        wizard = (
            self.env["stock.picking.cancel"]
            .with_context(active_ids=self.stock_picking.ids)
            .create({"reason_id": self.reason.id})
        )
        wizard.confirm_cancel()
        self.assertEqual(self.stock_picking.state, "cancel")
        self.assertEqual(self.stock_picking.cancel_reason_id, self.reason)
        self.assertFalse(self.stock_picking.cancel_description)

    def test_cancel_without_active_ids(self):
        wizard = (
            self.env["stock.picking.cancel"]
            .with_context(active_ids=None)
            .create({"reason_id": self.reason.id})
        )
        self.assertEqual(
            wizard.confirm_cancel(), {"type": "ir.actions.act_window_close"}
        )
        self.assertEqual(self.stock_picking.state, "draft")
        self.assertFalse(self.stock_picking.cancel_reason_id)

    def test_cancel_multiple_pickings(self):
        other_picking = self.stock_picking.copy()
        pickings = self.stock_picking | other_picking
        wizard = (
            self.env["stock.picking.cancel"]
            .with_context(active_ids=pickings.ids)
            .create({"reason_id": self.reason.id})
        )
        with self.assertRaisesRegex(AssertionError, "Only 1 picking ID expected"):
            wizard.confirm_cancel()
        self.assertEqual(set(pickings.mapped("state")), {"draft"})
        self.assertFalse(pickings.mapped("cancel_reason_id"))

    def test_reason_required(self):
        with self.assertRaises(AssertionError):
            Form(self.env["stock.picking.cancel"]).save()
