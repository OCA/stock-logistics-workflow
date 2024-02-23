# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestStockPickingBatchStart(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh = cls.env["stock.warehouse"].create(
            {
                "name": "Base Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "ship_only",
                "code": "BWH",
            }
        )
        cls.loc_stock = cls.wh.lot_stock_id
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Test product 1", "type": "product"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Test product 2", "type": "product"}
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type.id,
                "location_id": cls.loc_stock.id,
                "location_dest_id": cls.loc_customer.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "test move",
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 5,
                            "location_id": cls.loc_stock.id,
                            "location_dest_id": cls.loc_customer.id,
                        },
                    )
                ],
            }
        )

        cls.assigned_picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type.id,
                "location_id": cls.loc_stock.id,
                "location_dest_id": cls.loc_customer.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "test move",
                            "product_id": cls.product_2.id,
                            "product_uom_qty": 5,
                            "location_id": cls.loc_stock.id,
                            "location_dest_id": cls.loc_customer.id,
                        },
                    )
                ],
            }
        )
        cls._update_qty_in_location(cls.loc_stock, cls.product_2, 5)
        cls.assigned_picking.action_assign()
        cls.batch = cls.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set((cls.assigned_picking | cls.picking).ids)]}
        )
        cls.assigned_batch = cls.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set(cls.assigned_picking.ids)]}
        )
        cls.user = cls.env.user

    @classmethod
    def _update_qty_in_location(cls, location, product, quantity):
        quants = cls.env["stock.quant"]._gather(product, location, strict=True)
        # this method adds the quantity to the current quantity, so remove it
        quantity -= sum(quants.mapped("quantity"))
        cls.env["stock.quant"]._update_available_quantity(product, location, quantity)
        cls.env["product.product"].invalidate_model(
            fnames=[
                "qty_available",
                "virtual_available",
                "incoming_qty",
                "outgoing_qty",
            ]
        )

    def test_00(self):
        """test action start and user are propagated"""
        self.env.company.stock_picking_assign_operator_at_start = True
        self.assertFalse(self.batch.started)
        self.assertFalse(self.batch.action_start_allowed)
        self.assertFalse(self.batch.action_cancel_start_allowed)
        self.assertFalse(self.assigned_batch.started)
        self.assertTrue(self.assigned_batch.action_start_allowed)
        self.assertFalse(self.assigned_batch.action_cancel_start_allowed)
        self.assigned_batch.user_id = self.user
        self.assertFalse(self.assigned_picking.user_id)
        with self.assertRaises(
            UserError, msg="The following picking(s) can't be started"
        ):
            self.batch.action_start()
        with self.assertRaises(
            UserError,
            msg="he 'started' status of the following picking(s) can't be cancelled",
        ):
            self.batch.action_cancel_start()
        self.assigned_batch.action_start()
        self.assertTrue(self.assigned_batch.started)
        self.assertTrue(self.assigned_picking.started)
        self.assertTrue(self.assigned_batch.action_cancel_start_allowed)
        self.assertEqual(self.assigned_picking.user_id, self.user)
        self.assigned_batch.action_cancel_start()
        self.assertFalse(self.assigned_batch.started)
        self.assertFalse(self.assigned_picking.user_id)

    def test_01(self):
        """user is normally propagated to picking batch if the company setting is False"""
        self.env.company.stock_picking_assign_operator_at_start = False
        self.assertFalse(self.assigned_picking.user_id)
        self.assigned_batch.user_id = self.user
        self.assertEqual(self.assigned_picking.user_id, self.user)
        self.assigned_picking.user_id = False
        self.assertFalse(self.assigned_picking.user_id)
        self.env["stock.picking.batch"].create(
            {
                "picking_ids": [Command.set(self.assigned_picking.ids)],
                "user_id": self.user.id,
            }
        )
        self.assertEqual(self.assigned_picking.user_id, self.user)

    def test_02(self):
        """user is not propagated to picking batch if the company setting is False"""
        self.env.company.stock_picking_assign_operator_at_start = True
        self.assertFalse(self.assigned_picking.user_id)
        self.assigned_batch.user_id = self.user
        self.assertFalse(self.assigned_picking.user_id)
        self.assigned_picking.user_id = False
        self.assertFalse(self.assigned_picking.user_id)
        self.env["stock.picking.batch"].create(
            {
                "picking_ids": [Command.set(self.assigned_picking.ids)],
                "user_id": self.user.id,
            }
        )
        self.assertFalse(self.assigned_picking.user_id)
