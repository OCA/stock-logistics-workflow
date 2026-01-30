# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo.tests import Form, common
from odoo.tools import html2plaintext


class TestStockPickingReportCustomName(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Name",
                "default_code": "SPN",
                "type": "consu",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Test Name For Print",
                "default_code": "SPN",
                "type": "consu",
            }
        )
        cls.delivery_type = cls.env.ref("stock.picking_type_out")
        cls.picking_form = Form(cls.env["stock.picking"])
        cls.picking_form.picking_type_id = cls.env.ref("stock.picking_type_out")
        with cls.picking_form.move_ids_without_package.new() as move_form:
            move_form.product_id = cls.product
            move_form.quantity = 1
            move_form.product_uom_qty = 1
        cls.picking = cls.picking_form.save()

    def _get_report_in_plain_text(self):
        html, _ = self.env["ir.actions.report"]._render_qweb_html(
            "stock.action_report_delivery", self.picking.ids
        )
        return html2plaintext(html)

    def test_delivery_slip_without_move_line(self):
        self.picking.move_ids[0].display_in_report = False
        text = self._get_report_in_plain_text()
        self.assertFalse("Test Name" in text)
        self.assertFalse("Test Name For Print" in text)
