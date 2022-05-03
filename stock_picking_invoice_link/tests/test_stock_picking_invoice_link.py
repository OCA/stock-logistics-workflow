# Copyright 2016 Oihane Crucelaegui - AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# Copyright 2021 Tecnativa - João Marques
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo
from odoo.exceptions import UserError
from odoo.tests import Form

from odoo.addons.sale.tests.common import TestSaleCommon


@odoo.tests.tagged("-at_install", "post_install")
class TestStockPickingInvoiceLink(TestSaleCommon):
    def _update_product_qty(self, product):

        product_qty = self.env["stock.change.product.qty"].create(
            {
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "new_quantity": 100.0,
            }
        )
        product_qty.change_product_qty()
        return product_qty

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        for (_, i) in cls.company_data.items():
            if "type" in i and i.type == "product":
                cls._update_product_qty(i)
        cls.prod_order = cls.company_data["product_order_no"]
        cls.prod_del = cls.company_data["product_delivery_no"]
        cls.serv_order = cls.company_data["product_service_order"]
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_a.id,
                "partner_invoice_id": cls.partner_a.id,
                "partner_shipping_id": cls.partner_a.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.prod_order.name,
                            "product_id": cls.prod_order.id,
                            "product_uom_qty": 2,
                            "product_uom": cls.prod_order.uom_id.id,
                            "price_unit": cls.prod_order.list_price,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.prod_del.name,
                            "product_id": cls.prod_del.id,
                            "product_uom_qty": 2,
                            "product_uom": cls.prod_del.uom_id.id,
                            "price_unit": cls.prod_del.list_price,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.serv_order.name,
                            "product_id": cls.serv_order.id,
                            "product_uom_qty": 2,
                            "product_uom": cls.serv_order.uom_id.id,
                            "price_unit": cls.serv_order.list_price,
                        },
                    ),
                ],
                "pricelist_id": cls.env.ref("product.list0").id,
                "picking_policy": "direct",
            }
        )
        cls.so.action_confirm()

    def test_00_sale_stock_invoice_link(self):
        pick_obj = self.env["stock.picking"]
        # invoice on order
        self.so._create_invoices()
        # deliver partially
        self.assertEqual(
            self.so.invoice_status,
            "no",
            "Sale Stock: so invoice_status should be "
            '"nothing to invoice" after invoicing',
        )
        pick_1 = self.so.picking_ids.filtered(
            lambda x: x.picking_type_code == "outgoing"
            and x.state in ("confirmed", "assigned")
        )
        pick_1.move_line_ids.write({"qty_done": 1})
        pick_1._action_done()
        self.assertEqual(
            self.so.invoice_status,
            "to invoice",
            "Sale Stock: so invoice_status should be "
            '"to invoice" after partial delivery',
        )
        inv_1 = self.so._create_invoices()
        # complete the delivery
        self.assertEqual(
            self.so.invoice_status,
            "no",
            "Sale Stock: so invoice_status should be "
            '"nothing to invoice" after partial delivery '
            "and invoicing",
        )
        self.assertEqual(
            len(self.so.picking_ids), 2, "Sale Stock: number of pickings should be 2"
        )

        pick_2 = self.so.picking_ids.filtered(
            lambda x: x.picking_type_code == "outgoing"
            and x.state in ("confirmed", "assigned")
        )
        pick_2.move_line_ids.write({"qty_done": 1})
        pick_2._action_done()
        backorders = pick_obj.search([("backorder_id", "=", pick_2.id)])
        self.assertFalse(
            backorders,
            "Sale Stock: second picking should be "
            "final without need for a backorder",
        )
        self.assertEqual(
            self.so.invoice_status,
            "to invoice",
            "Sale Stock: so invoice_status should be "
            '"to invoice" after complete delivery',
        )
        inv_2 = self.so._create_invoices()
        self.assertEqual(
            self.so.invoice_status,
            "invoiced",
            "Sale Stock: so invoice_status should be "
            '"fully invoiced" after complete delivery and '
            "invoicing",
        )
        # Check links
        self.assertEqual(
            inv_1.picking_ids,
            pick_1,
            "Invoice 1 must link to only First Partial Delivery",
        )
        self.assertEqual(
            inv_1.invoice_line_ids.mapped("move_line_ids"),
            pick_1.move_lines.filtered(
                lambda x: x.product_id.invoice_policy == "delivery"
            ),
            "Invoice 1 lines must link to only First Partial Delivery lines",
        )
        self.assertEqual(
            inv_2.picking_ids, pick_2, "Invoice 2 must link to only Second Delivery"
        )
        self.assertEqual(
            inv_2.invoice_line_ids.mapped("move_line_ids"),
            pick_2.move_lines.filtered(
                lambda x: x.product_id.invoice_policy == "delivery"
            ),
            "Invoice 2 lines must link to only Second Delivery lines",
        )
        # Invoice view
        result = pick_1.action_view_invoice()
        self.assertEqual(result["views"][0][1], "form")
        self.assertEqual(result["res_id"], inv_1.id)
        # Mock multiple invoices linked to a picking
        inv_3 = inv_1.copy()
        inv_3.picking_ids |= pick_1
        result = pick_1.action_view_invoice()
        self.assertEqual(result["views"][0][1], "tree")

        # Cancel invoice and invoice
        inv_1.button_cancel()
        self.so._create_invoices()
        self.assertEqual(
            inv_1.picking_ids,
            pick_1,
            "Invoice 1 must link to only First Partial Delivery",
        )
        self.assertEqual(
            inv_1.invoice_line_ids.mapped("move_line_ids"),
            pick_1.move_lines.filtered(
                lambda x: x.product_id.invoice_policy == "delivery"
            ),
            "Invoice 1 lines must link to only First Partial Delivery lines",
        )
        # Try to update a picking move which has a invoice line linked
        with self.assertRaises(UserError):
            pick_1.move_line_ids.write({"qty_done": 20.0})

    def test_return_picking_to_refund(self):
        pick_1 = self.so.picking_ids.filtered(
            lambda x: x.picking_type_code == "outgoing"
            and x.state in ("confirmed", "assigned")
        )
        pick_1.move_line_ids.write({"qty_done": 2})
        pick_1._action_done()

        # Create invoice
        inv = self.so._create_invoices()
        inv_line_prod_del = inv.invoice_line_ids.filtered(
            lambda l: l.product_id == self.prod_del
        )
        self.assertEqual(
            inv_line_prod_del.move_line_ids,
            pick_1.move_lines.filtered(lambda m: m.product_id == self.prod_del),
        )
        # Create return picking
        return_form = Form(self.env["stock.return.picking"])
        return_form.picking_id = pick_1
        return_wiz = return_form.save()

        # Remove product ordered line
        return_wiz.product_return_moves.filtered(
            lambda l: l.product_id == self.prod_order
        ).unlink()
        return_wiz.product_return_moves.quantity = 1.0
        return_wiz.product_return_moves.to_refund = True
        res = return_wiz.create_returns()
        return_pick = self.env["stock.picking"].browse(res["res_id"])
        # Validate picking
        return_pick.move_lines.quantity_done = 1.0
        return_pick.button_validate()
        inv = self.so._create_invoices(final=True)
        inv_line_prod_del = inv.invoice_line_ids.filtered(
            lambda l: l.product_id == self.prod_del
        )
        self.assertEqual(inv_line_prod_del.move_line_ids, return_pick.move_lines)

    def test_invoice_refund(self):
        pick_1 = self.so.picking_ids.filtered(
            lambda x: x.picking_type_code == "outgoing"
            and x.state in ("confirmed", "assigned")
        )
        pick_1.move_line_ids.write({"qty_done": 2})
        pick_1._action_done()
        # Create invoice
        inv = self.so._create_invoices()
        inv.action_post()
        move_line_prod_del = pick_1.move_lines.filtered(
            lambda l: l.product_id == self.prod_del
        )
        wiz_invoice_refund = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=inv.ids)
            .create({"refund_method": "modify", "reason": "test"})
        )
        wiz_invoice_refund.reverse_moves()
        new_invoice = self.so.invoice_ids.filtered(
            lambda i: i.move_type == "out_invoice" and i.state == "draft"
        )
        inv_line_prod_del = new_invoice.invoice_line_ids.filtered(
            lambda l: l.product_id == self.prod_del
        )
        self.assertEqual(move_line_prod_del, inv_line_prod_del.move_line_ids)

        # Test action open picking from an invoice
        res = new_invoice.action_show_picking()
        opened_picking = self.env["stock.picking"].browse(res["res_id"])
        self.assertEqual(pick_1, opened_picking)
