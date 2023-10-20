# Copyright 2022 Tecnativa - Sergio Teruel
# Copyright 2023 Moduon Team - Eduardo de Miguel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import Form, TransactionCase


class TestStockPickingBatchExtendedAccount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env["sale.order"]
        cls.product_uom_id = cls.env.ref("uom.product_uom_unit")
        cls.stock_loc = cls.browse_ref(cls, "stock.stock_location_stock")
        cls.currency_usd = cls.env.ref("base.USD")
        cls.currency_usd.active = True
        # Make sure the currency of the company is USD, as this not always happens
        # To be removed in V17: https://github.com/odoo/odoo/pull/107113
        cls.company = cls.env.company
        cls.env.cr.execute(
            "UPDATE res_company SET currency_id = %s WHERE id = %s",
            [cls.currency_usd.id, cls.company.id],
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "test",
                "type": "product",
                "list_price": 20.00,
                "invoice_policy": "delivery",
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "product_uom_id": cls.product.uom_id.id,
                "location_id": cls.stock_loc.id,
                "quantity": 100.0,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "partner test 1", "batch_picking_auto_invoice": "no"}
        )
        cls.partner2 = cls.env["res.partner"].create(
            {"name": "partner test 2", "batch_picking_auto_invoice": "no"}
        )

    def _create_sale_order(self, partner):
        with Form(self.env["sale.order"]) as so_form:
            so_form.partner_id = partner
            with so_form.order_line.new() as line_form:
                line_form.product_id = self.product
                line_form.product_uom_qty = 1.0
        return so_form.save()

    def _create_batch_picking(self, pickings):
        # Create the BP
        with Form(
            self.env["stock.picking.to.batch"].with_context(
                active_ids=pickings.ids, active_model="stock.picking"
            )
        ) as wiz_form:
            wiz_form.mode = "new"
        wiz = wiz_form.save()
        wiz.attach_pickings()
        return pickings.mapped("batch_id")

    def _process_immediate_transfer(self, res_action):
        sit_model = self.env[res_action["res_model"]].with_context(
            **res_action["context"]
        )
        immediate_transfer_wiz_vals = sit_model.default_get(
            [
                "pick_ids",
                "show_transfers",
                "immediate_transfer_line_ids",
            ]
        )
        wiz = sit_model.create(immediate_transfer_wiz_vals)
        return wiz.process()

    def test_create_invoice_from_bp_no_invoices(self):
        self.partner.batch_picking_auto_invoice = "no"
        self.partner2.batch_picking_auto_invoice = "no"
        self.order1 = self._create_sale_order(self.partner)
        self.order2 = self._create_sale_order(self.partner2)
        self.order1.action_confirm()
        self.order2.action_confirm()
        pickings = self.order1.picking_ids + self.order2.picking_ids
        move_lines = pickings.mapped("move_line_ids")
        move_lines.qty_done = 1.0
        bp = self._create_batch_picking(pickings)
        bp.action_assign()
        action_done_res = bp.action_done()
        if action_done_res is not True:
            self._process_immediate_transfer(action_done_res)
        self.assertFalse(self.order1.invoice_ids)
        self.assertFalse(self.order2.invoice_ids)

    def test_create_invoice_from_bp_all_invoices(self):
        self.partner.batch_picking_auto_invoice = "yes"
        self.partner2.batch_picking_auto_invoice = "yes"
        self.order1 = self._create_sale_order(self.partner)
        self.order2 = self._create_sale_order(self.partner2)
        self.order1.action_confirm()
        self.order2.action_confirm()
        pickings = self.order1.picking_ids + self.order2.picking_ids
        move_lines = pickings.mapped("move_line_ids")
        move_lines.qty_done = 1.0
        bp = self._create_batch_picking(pickings)
        bp.action_assign()
        action_done_res = bp.action_done()
        if action_done_res is not True:
            self._process_immediate_transfer(action_done_res)
        self.assertTrue(self.order1.invoice_ids)
        self.assertTrue(self.order2.invoice_ids)

    def test_create_invoice_from_bp_mixin(self):
        self.partner.batch_picking_auto_invoice = "yes"
        self.partner2.batch_picking_auto_invoice = "no"
        self.order1 = self._create_sale_order(self.partner)
        self.order2 = self._create_sale_order(self.partner2)
        self.order1.action_confirm()
        self.order2.action_confirm()
        pickings = self.order1.picking_ids + self.order2.picking_ids
        move_lines = pickings.mapped("move_line_ids")
        move_lines.qty_done = 1.0
        bp = self._create_batch_picking(pickings)
        bp.action_assign()
        action_done_res = bp.action_done()
        if action_done_res is not True:
            self._process_immediate_transfer(action_done_res)
        self.assertTrue(self.order1.invoice_ids)
        self.assertFalse(self.order2.invoice_ids)
