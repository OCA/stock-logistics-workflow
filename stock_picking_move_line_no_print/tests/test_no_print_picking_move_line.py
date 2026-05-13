# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo.tests import Form, common


class TestStockPickingReportCustomName(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Name P1",
                "default_code": "SPN1",
                "type": "consu",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Test Name P2",
                "default_code": "SPN2",
                "type": "consu",
            }
        )
        cls.delivery_type = cls.env.ref("stock.picking_type_out")
        cls.picking_form = Form(cls.env["stock.picking"])
        cls.picking_form.picking_type_id = cls.env.ref("stock.picking_type_out")
        with cls.picking_form.move_ids.new() as move_form:
            move_form.product_id = cls.product
            move_form.quantity = 1
            move_form.product_uom_qty = 1
            move_form.display_in_report = False
        with cls.picking_form.move_ids.new() as move_form:
            move_form.product_id = cls.product_2
            move_form.quantity = 1
            move_form.product_uom_qty = 1
            move_form.display_in_report = True
        cls.picking = cls.picking_form.save()

    def _get_report_in_plain_text(self):
        txt, _ = self.env["ir.actions.report"]._render_qweb_text(
            "stock.report_deliveryslip", self.picking.ids
        )
        return txt.decode("utf-8")

    def test_delivery_slip_without_move(self):
        self.assertNotEqual(self.picking.state, "done")
        text = self._get_report_in_plain_text()
        self.assertFalse("Test Name P1" in text)
        self.assertTrue("Test Name P2" in text)

    def test_delivery_slip_without_move_line(self):
        self.picking.button_validate()
        self.assertEqual(self.picking.state, "done")
        text = self._get_report_in_plain_text()
        # print(text)
        self.assertFalse("Test Name P1" in text)
        self.assertTrue("Test Name P2" in text)
