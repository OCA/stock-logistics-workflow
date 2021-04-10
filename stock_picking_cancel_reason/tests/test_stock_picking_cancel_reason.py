# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestStockPickingCancelReason(TransactionCase):
    def setUp(self):
        super(TestStockPickingCancelReason, self).setUp()
        StockPicking = self.env["stock.picking"]
        CancelReason = self.env["stock.picking.cancel.reason"]
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        picking_type_out = self.env.ref("stock.picking_type_out")
        stock_location = self.env.ref("stock.stock_location_stock")
        customer_location = self.env.ref("stock.stock_location_customers")
        self.reason = CancelReason.create({"name": "Canceled for tests"})
        self.product = self.env["product.product"].create({"name": "Product"})
        # create a picking out
        self.stock_picking = StockPicking.create(
            {
                "partner_id": partner.id,
                "picking_type_id": picking_type_out.id,
                "location_id": stock_location.id,
                "location_dest_id": customer_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 10,
                            "product_uom": self.product.uom_id.id,
                            "location_id": stock_location.id,
                            "location_dest_id": customer_location.id,
                        },
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
        wizard = StockPickingCancel.create({"reason_id": self.reason.id})
        wizard.with_context(context).confirm_cancel()
        self.assertEqual(
            self.stock_picking.state, "cancel", "the stock picking should be canceled"
        )
        self.assertEqual(self.stock_picking.cancel_reason_id.id, self.reason.id)
