# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestRestrictCancelStockMove(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write({"reception_steps": "three_steps"})
        cls.stock_loc = cls.warehouse.lot_stock_id
        cls.input_loc = cls.warehouse.wh_input_stock_loc_id
        cls.qc_loc = cls.warehouse.wh_qc_stock_loc_id
        cls.internal_pt = cls.warehouse.int_type_id
        cls.internal_pt.active = True
        cls.internal_pt.restrict_cancel_with_orig_move = True
        # Create a vendor
        partner = cls.env["res.partner"].create({"name": "Smith"})
        # Create product and set the default vendor
        product_form = Form(cls.env["product.product"])
        product_form.name = "Product A"
        product_form.type = "consu"
        product_form.is_storable = "True"
        product_form.purchase_ok = True
        with product_form.seller_ids.new() as seller:
            seller.partner_id = partner
        product_form.route_ids.add(cls.env.ref("purchase_stock.route_warehouse0_buy"))
        cls.dummy_product = product_form.save()
        # Create product reordering rule
        cls.order_point = cls.env["stock.warehouse.orderpoint"].create(
            {
                "name": f"OP-{cls.dummy_product.name}",
                "warehouse_id": cls.warehouse.id,
                "location_id": cls.stock_loc.id,
                "product_id": cls.dummy_product.id,
                "product_min_qty": 1.0,
                "product_max_qty": 10.0,
            }
        )

    def test_restrict(self):
        # Run scheduler, this should create a new RFQ
        self.env["procurement.group"].run_scheduler()
        rfqs = (
            self.env["purchase.order.line"]
            .search([("product_id", "=", self.dummy_product.id)])
            .order_id.filtered(lambda po: po.state in ("draft", "sent", "to approve"))
        )
        rfqs.button_confirm()
        receipt_move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.dummy_product.id),
                ("location_dest_id", "=", self.input_loc.id),
            ]
        )
        self.assertNotEqual(receipt_move.state, "cancel")
        # Manually create the next leg (Input -> QC), linked to that receipt
        # move as its origin, to test cancelling it while the PO receipt is
        # not done yet.
        input_to_qc_picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.internal_pt.id,
                "location_id": self.input_loc.id,
                "location_dest_id": self.qc_loc.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.dummy_product.name,
                            "product_id": self.dummy_product.id,
                            "product_uom": self.dummy_product.uom_id.id,
                            "product_uom_qty": 10,
                            "location_id": self.input_loc.id,
                            "location_dest_id": self.qc_loc.id,
                        },
                    )
                ],
            }
        )
        input_to_qc_picking.action_confirm()
        input_to_qc_picking.move_ids.move_orig_ids |= receipt_move
        receipt_move.created_purchase_line_ids = [Command.link(rfqs.order_line.id)]
        self.assertNotEqual(input_to_qc_picking.move_ids.state, "cancel")
        with self.assertRaises(UserError) as cm:
            input_to_qc_picking.action_cancel()
        self.assertIn(rfqs.order_line.name, str(cm.exception))
