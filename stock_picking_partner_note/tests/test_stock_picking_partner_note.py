# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, common

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class StockPickingPartnerNote(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env
        cls.product_a = cls.env.ref("product.product_product_4")
        cls.note_type1 = cls.env["stock.picking.note.type"].create(
            {"name": "Note type 1", "sequence": 10}
        )
        cls.note_type2 = cls.env["stock.picking.note.type"].create(
            {"name": "Note type 2", "sequence": 20}
        )
        cls.partner_a = cls.env["res.partner"].create(
            {
                "name": "Customer A",
                "stock_picking_note_ids": [
                    (0, 0, {"name": "Note 1    ", "note_type_id": cls.note_type1.id}),
                    (0, 0, {"name": "Note 2", "note_type_id": cls.note_type2.id}),
                    (0, 0, {"name": "   ", "note_type_id": cls.note_type2.id}),
                ],
            }
        )

    def test_picking_partner_note(self):
        with Form(self.env["sale.order"]) as order_form:
            order_form.partner_id = self.partner_a
            with order_form.order_line.new() as line_form:
                line_form.product_id = self.product_a
                line_form.product_uom_qty = 1

        self.order = order_form.save()
        self.order.warehouse_id.out_type_id.partner_note_type_ids = [
            (6, 0, (self.note_type1 | self.note_type2).ids)
        ]
        self.order.action_confirm()
        self.assertIn("<p>Note 1<br>Note 2</p>", self.order.picking_ids[0].note)
