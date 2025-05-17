# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestMassAction(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "product",
            }
        )
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.lot1 = cls.env["stock.lot"].create(
            {
                "name": "lot1",
                "product_id": cls.product.id,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.stock_location, 600.0, lot_id=cls.lot1
        )

        # Force Odoo not to automatically reserve the products on the pickings
        # so we can test stock.picking.mass.action
        cls.picking_type_out.reservation_method = "manual"
        # We create a picking out
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.picking_type_out.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 200,
                            "product_uom": cls.product.uom_id.id,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    )
                ],
            }
        )

    def test_mass_action(self):
        self.assertEqual(self.picking.state, "draft")
        wiz = self.env["stock.picking.mass.action"]
        # We test confirming a picking
        wiz_confirm = wiz.create({"picking_ids": [Command.link(self.picking.id)]})
        wiz_confirm.confirm = True
        wiz_confirm.mass_action()
        self.assertEqual(self.picking.state, "confirmed")
        # We test transferring picking
        wiz_tranfer = wiz.with_context(transfer=True).create(
            {"picking_ids": [Command.link(self.picking.id)]}
        )
        wiz_tranfer.confirm = True
        for line in self.picking.move_ids:
            line.quantity = line.product_uom_qty
            line.picked = True
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
        wiz_confirm = wiz.create({"picking_ids": [Command.set([pick1.id, pick2.id])]})
        wiz_confirm.confirm = True
        wiz_confirm.mass_action()
        self.assertEqual(pick1.state, "confirmed")
        self.assertEqual(pick2.state, "confirmed")
        pickings.check_assign_all()
        self.assertEqual(pick1.state, "assigned")
        self.assertEqual(pick2.state, "assigned")

        pick3 = self.picking.copy()
        pickings |= pick3
        pick4 = self.picking.copy()
        pickings |= pick4
        self.assertEqual(pick3.state, "draft")
        self.assertEqual(pick4.state, "draft")
        wiz_confirm = wiz.create({"picking_ids": [Command.set([pick3.id, pick4.id])]})
        wiz_confirm.confirm = True
        wiz_confirm.mass_action()
        self.assertEqual(pick3.state, "confirmed")
        self.assertEqual(pick4.state, "confirmed")
        pickings.check_assign_all(domain=[("picking_type_code", "=", "outgoing")])
        self.assertEqual(pick1.state, "assigned")
        self.assertEqual(pick2.state, "assigned")

    def test_mass_action_immediate_transfer(self):
        wiz_tranfer = self.env["stock.picking.mass.action"].create(
            {
                "picking_ids": [Command.link(self.picking.id)],
                "confirm": True,
                "transfer": True,
            }
        )
        wiz_tranfer.mass_action()
        self.picking.check_assign_all()
        self.assertEqual(self.picking.move_ids.quantity, 200)
        # Check move_lines data
        self.assertEqual(len(self.picking.move_ids.move_line_ids), 1)
        self.assertEqual(self.picking.move_ids.move_line_ids.quantity, 200)
        # Check quants data
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.product, self.stock_location
            ),
            400.0,
        )

    def test_mass_action_backorder(self):
        wiz_tranfer = self.env["stock.picking.mass.action"].create(
            {
                "picking_ids": [Command.link(self.picking.id)],
                "confirm": True,
                "transfer": True,
            }
        )
        self.picking.action_assign()
        self.picking.move_ids[0].quantity = 30
        res = wiz_tranfer.mass_action()
        self.assertEqual(res["res_model"], "stock.backorder.confirmation")
