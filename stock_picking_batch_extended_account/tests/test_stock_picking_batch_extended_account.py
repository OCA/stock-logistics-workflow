# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import Form, TransactionCase


class TestStockPickingBatchExtendedAccount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
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
            [cls.env.ref("base.USD").id, cls.company.id],
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
        # Use OCA batch picking extended
        cls.env.company.use_oca_batch_validation = True

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
                active_ids=pickings.ids, active_model="sotck.picking"
            )
        ) as wiz_form:
            wiz_form.name = "BP for test"
            wiz_form.mode = "new"
        wiz = wiz_form.save()
        action = wiz.action_create_batch()
        return self.env["stock.picking.batch"].browse(action["res_id"])

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
        bp.action_done()
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
        bp.action_done()
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
        bp.action_done()
        self.assertTrue(self.order1.invoice_ids)
        self.assertFalse(self.order2.invoice_ids)
