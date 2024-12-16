# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields
from odoo.tests import common


class TestMassAction(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        partner = cls.env["res.partner"].create({"name": "Test Partner"})
        product = cls.env["product.product"].create(
            {"name": "Product Test", "type": "product"}
        )
        picking_type_out = cls.env.ref("stock.picking_type_out")
        stock_location = cls.env.ref("stock.stock_location_stock")
        customer_location = cls.env.ref("stock.stock_location_customers")
        cls.env["stock.quant"].create(
            {
                "product_id": product.id,
                "location_id": stock_location.id,
                "quantity": 900,
            }
        )
        # Force Odoo not to automatically reserve the products on the pickings
        # so we can test stock.picking.mass.action
        picking_type_out.reservation_method = "manual"
        # We create a picking out
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": partner.id,
                "picking_type_id": picking_type_out.id,
                "location_id": stock_location.id,
                "location_dest_id": customer_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": 200,
                            "product_uom": product.uom_id.id,
                            "location_id": stock_location.id,
                            "location_dest_id": customer_location.id,
                        },
                    )
                ],
            }
        )

    def test_mass_action(self):
        """
        Test manual assignment of pickings
        """
        self.assertEqual(self.picking.state, "draft")
        wiz = self.env["stock.picking.mass.action"]
        # We test confirming a picking
        wiz_confirm = wiz.create({"picking_ids": [(4, self.picking.id)]})
        wiz_confirm.confirm = True
        wiz_confirm.mass_action()
        self.assertEqual(self.picking.state, "confirmed")
        # We test transferring picking
        wiz_tranfer = wiz.with_context(transfer=True).create(
            {"picking_ids": [(4, self.picking.id)]}
        )
        wiz_tranfer.confirm = True
        for line in self.picking.move_ids:
            line.quantity_done = line.product_uom_qty
        wiz_tranfer.mass_action()
        self.assertEqual(self.picking.state, "done")
        # We test checking assign all
        pickings = self.env["stock.picking"]
        pick1 = self.picking.copy()
        pickings |= pick1
        pick2 = self.picking.copy()
        pickings |= pick2
        self.assertEqual(pick1.state, "draft")
        self.assertEqual(pick2.state, "draft")
        wiz_confirm = wiz.create({"picking_ids": [(6, 0, [pick1.id, pick2.id])]})
        wiz_confirm.confirm = True
        wiz_confirm.mass_action()
        self.assertEqual(pick1.state, "confirmed")
        self.assertEqual(pick2.state, "confirmed")
        # Confirm pickings are not assigned automatically
        pickings.check_assign_all()
        self.assertEqual(pick1.state, "confirmed")
        self.assertEqual(pick2.state, "confirmed")
        pick3 = self.picking.copy()
        pickings |= pick3
        pick4 = self.picking.copy()
        pickings |= pick4
        self.assertEqual(pick3.state, "draft")
        self.assertEqual(pick4.state, "draft")
        wiz_confirm = wiz.create({"picking_ids": [(6, 0, [pick3.id, pick4.id])]})
        wiz_confirm.confirm = True
        wiz_confirm.mass_action()
        self.assertEqual(pick3.state, "confirmed")
        self.assertEqual(pick4.state, "confirmed")
        pickings.check_assign_all(domain=[("picking_code", "=", "outgoing")])
        self.assertEqual(pick3.state, "confirmed")
        self.assertEqual(pick4.state, "confirmed")
        # Confirm pickings are assigned manually
        pick1.action_assign()
        pick2.action_assign()
        self.assertEqual(pick1.state, "assigned")
        self.assertEqual(pick2.state, "assigned")
        pick3.action_assign()
        pick4.action_assign()
        self.assertEqual(pick3.state, "assigned")
        self.assertEqual(pick4.state, "assigned")

    def test_at_confirm_reservation(self):
        """
        Test automatically reservation at picking confirmation
        """
        # Set at_confirm method
        self.env.ref("stock.picking_type_out").write(
            {"reservation_method": "at_confirm"}
        )
        self.assertEqual(self.picking.state, "draft")
        for line in self.picking.move_ids:
            self.assertEqual(line.state, "draft")
        self.picking.action_confirm()
        self.assertEqual(self.picking.state, "assigned")
        for line in self.picking.move_ids:
            self.assertEqual(line.state, "assigned")
            self.assertEqual(line.reserved_availability, 200.0)

    def test_mass_action_by_date(self):
        """
        Test automatically reservation by date
        """
        # Set by date method
        self.env.ref("stock.picking_type_out").write(
            {"reservation_method": "by_date", "reservation_days_before": 4}
        )
        self.assertEqual(self.picking.state, "draft")
        wiz = self.env["stock.picking.mass.action"]
        # We test checking assign all with "by date" method
        pickings = self.env["stock.picking"]
        pickOutDate = self.picking.copy()
        # Set scheduled date out of the range of 4 days
        pickOutDate.scheduled_date = fields.Date.today() + timedelta(days=15)
        pickings |= pickOutDate
        pickInDate = self.picking.copy()
        pickings |= pickInDate
        self.assertEqual(pickOutDate.state, "draft")
        self.assertEqual(pickInDate.state, "draft")
        wiz_confirm = wiz.create(
            {"picking_ids": [(6, 0, [pickOutDate.id, pickInDate.id])]}
        )
        wiz_confirm.confirm = True
        wiz_confirm.mass_action()
        self.assertEqual(pickOutDate.state, "confirmed")
        self.assertEqual(pickInDate.state, "assigned")
        pickings.check_assign_all()
        self.assertEqual(pickOutDate.state, "confirmed")
        # Change scheduled date in the range of 4 days
        pickOutDate.scheduled_date = fields.Date.today() + timedelta(days=1)
        pickings.check_assign_all()
        self.assertEqual(pickOutDate.state, "assigned")

    def test_mass_action_inmediate_transfer(self):
        wiz_tranfer = self.env["stock.picking.mass.action"].create(
            {"picking_ids": [(4, self.picking.id)], "confirm": True, "transfer": True}
        )
        res = wiz_tranfer.mass_action()
        self.assertEqual(res["res_model"], "stock.immediate.transfer")

    def test_mass_action_backorder(self):
        wiz_tranfer = self.env["stock.picking.mass.action"].create(
            {"picking_ids": [(4, self.picking.id)], "confirm": True, "transfer": True}
        )
        self.picking.action_assign()
        self.picking.move_ids[0].quantity_done = 30
        res = wiz_tranfer.mass_action()
        self.assertEqual(res["res_model"], "stock.backorder.confirmation")
