# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockPickingMRPProductionOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking = cls.env.ref("stock.incomming_shipment1")
        cls.picking2 = cls.env.ref("stock.incomming_shipment2")
        cls.mrp_mass_order_entry = cls.env["mrp.mass.production.order.entry.wizard"]
        cls.Product = cls.env["product.product"]
        cls.Bom = cls.env["mrp.bom"]
        cls.BomLine = cls.env["mrp.bom.line"]
        cls.Picking = cls.env["stock.picking"]
        cls.Move = cls.env["stock.move"]
        cls.MrpProduction = cls.env["mrp.production"]
        cls.Wizard = cls.env["mrp.mass.production.order.wizard"]

        # Create products
        cls.product_a = cls.Product.create({"name": "Product A"})
        cls.product_b = cls.Product.create({"name": "Product B"})
        cls.product_c = cls.Product.create({"name": "Product C"})

        # Create BOM and BOM lines
        cls.bom = cls.Bom.create({"product_tmpl_id": cls.product_a.product_tmpl_id.id})
        cls.bom_line_a = cls.BomLine.create(
            {"bom_id": cls.bom.id, "product_id": cls.product_b.id, "product_qty": 2}
        )
        cls.bom_line_b = cls.BomLine.create(
            {"bom_id": cls.bom.id, "product_id": cls.product_c.id, "product_qty": 1}
        )

        # Create picking and moves
        cls.move_b = cls.Move.create(
            {
                "picking_id": cls.picking.id,
                "product_id": cls.product_b.id,
                "product_uom_qty": 10,
                "location_id": cls.picking.location_id.id,
                "location_dest_id": cls.picking.location_dest_id.id,
                "consumed_quantity": 0,
                "name": "Move B",
            }
        )
        cls.move_c = cls.Move.create(
            {
                "picking_id": cls.picking.id,
                "product_id": cls.product_c.id,
                "product_uom_qty": 5,
                "consumed_quantity": 0,
                "location_id": cls.picking.location_id.id,
                "location_dest_id": cls.picking.location_dest_id.id,
                "name": "Move A",
            }
        )

        # # Create picking and moves
        # cls.move1 = cls.Move.create(
        #     {
        #         "picking_id": cls.picking.id,
        #         "product_id": cls.product2.id,
        #         "product_uom_qty": 10,
        #         "consumed_quantity": 0,
        #         "location_id": cls.picking.location_id.id,
        #         "location_dest_id": cls.picking.location_dest_id.id,
        #         "name": "Move 1",
        #     }
        # )
        # cls.move2 = cls.Move.create(
        #     {
        #         "picking_id": cls.picking.id,
        #         "product_id": cls.product3.id,
        #         "product_uom_qty": 5,
        #         "consumed_quantity": 0,
        #         "location_id": cls.picking.location_id.id,
        #         "location_dest_id": cls.picking.location_dest_id.id,
        #         "name": "Move 2",
        #     }
        # )

    def test_mass_production_from_picking(self):
        with self.assertRaises(ValidationError):
            self.picking.action_mrp_mass_production_order()
        self.picking.button_validate()
        action = self.picking.action_mrp_mass_production_order()
        default_entries = action["context"]["default_mrp_production_order_entries"]
        entry = self.mrp_mass_order_entry.browse(default_entries)
        entry.quantity = 50.0
        order_wizard = self.env["mrp.mass.production.order.wizard"].create(
            {"with_bom": False}
        )
        entry.mrp_production_order_entry_id = order_wizard.id
        with self.assertRaises(ValidationError):
            entry.mrp_production_order_entry_id.with_context(
                active_model="stock.picking", active_id=self.picking.id
            ).action_create()
        entry.quantity = 5.0
        entry.mrp_production_order_entry_id.with_context(
            active_model="stock.picking", active_id=self.picking.id
        ).action_create()
        self.assertEqual(entry.product_consumed_id, self.picking.move_ids.product_id)
        self.assertEqual(len(default_entries), 3)
        self.assertEqual(self.picking.mrp_picking_count, 3)

    def test_action_create_with_bom_success(self):
        wizard = self.Wizard.with_context(
            active_model="stock.picking", active_id=self.picking.id
        ).create(
            {
                "with_bom": True,
                "mrp_production_order_entries": [
                    (
                        0,
                        0,
                        {
                            "bom_id": self.bom.id,
                            "product_id": self.product_a.id,
                            "product_qty": 2,
                        },
                    )
                ],
            }
        )
        res = wizard.action_create()
        self.assertIsInstance(res, dict)

    def test_action_create_with_bom_missing_product(self):
        # Remove product_c from picking
        self.picking.move_ids.filtered(
            lambda m: m.product_id == self.product_c
        ).unlink()
        wizard = self.Wizard.with_context(
            active_model="stock.picking", active_id=self.picking.id
        ).create(
            {
                "with_bom": True,
                "mrp_production_order_entries": [
                    (
                        0,
                        0,
                        {
                            "bom_id": self.bom.id,
                            "product_qty": 1,
                            "product_id": self.product_a.id,
                        },
                    )
                ],
            }
        )
        with self.assertRaises(ValidationError):
            wizard.action_create()

    def test_action_create_without_product_to_consume(self):
        for move in self.picking.move_ids:
            move.consumed_quantity = move.product_uom_qty

        self.picking.button_validate()
        with self.assertRaises(
            ValidationError, msg=_("There are no products to consume")
        ):
            self.picking.action_mrp_mass_production_order()

    def test_action_create_with_bom_exceed_quantity(self):
        # Set consumed_quantity to near limit
        self.move_b.consumed_quantity = 9
        wizard = self.Wizard.with_context(
            active_model="stock.picking", active_id=self.picking.id
        ).create(
            {
                "with_bom": True,
                "mrp_production_order_entries": [
                    (
                        0,
                        0,
                        {
                            "bom_id": self.bom.id,
                            "product_qty": 1,
                            "product_id": self.product_a.id,
                        },
                    )
                ],
            }
        )
        with self.assertRaises(ValidationError):
            wizard.action_create()

    def test_action_create_without_bom_success(self):
        wizard = self.Wizard.with_context(
            active_model="stock.picking", active_id=self.picking.id
        ).create(
            {
                "with_bom": False,
                "mrp_production_order_entries": [
                    (
                        0,
                        0,
                        {
                            "product_consumed_id": self.product_b.id,
                            "product_id": self.product_a.id,
                            "quantity": 2,
                        },
                    )
                ],
            }
        )
        res = wizard.action_create()
        self.assertIsInstance(res, dict)

    def test_action_create_without_bom_missing_product(self):
        wizard = self.Wizard.with_context(
            active_model="stock.picking", active_id=self.picking.id
        ).create(
            {
                "with_bom": False,
                "mrp_production_order_entries": [
                    (
                        0,
                        0,
                        {
                            "product_consumed_id": self.env["product.product"]
                            .create({"name": "Missing"})
                            .id,
                            "quantity": 1,
                            "product_id": self.product_a.id,
                        },
                    )
                ],
            }
        )
        with self.assertRaises(ValidationError):
            wizard.action_create()

    def test_action_create_without_bom_exceed_quantity(self):
        self.move_b.consumed_quantity = 9
        wizard = self.Wizard.with_context(
            active_model="stock.picking", active_id=self.picking.id
        ).create(
            {
                "with_bom": False,
                "mrp_production_order_entries": [
                    (
                        0,
                        0,
                        {
                            "product_consumed_id": self.product_b.id,
                            "quantity": 2,
                            "product_id": self.product_a.id,
                        },
                    )
                ],
            }
        )
        with self.assertRaises(ValidationError):
            wizard.action_create()
