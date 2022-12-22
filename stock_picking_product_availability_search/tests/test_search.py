# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import TransactionCase


class TestSearch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product = cls.env["product.product"].create(
            {"name": "Product", "type": "product"}
        )
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.location_customers = cls.env.ref("stock.stock_location_customers")
        cls.location_suppliers = cls.env.ref("stock.stock_location_suppliers")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        # Create some initial stocks
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "product_uom_id": cls.product.uom_id.id,
                "location_id": cls.location_stock.id,
                "quantity": 10.00,
            }
        )
        # Create some incoming pickings
        cls.picking_in_draft = cls._create_picking(picking_type="in", confirm=False)
        cls.picking_in_confirm = cls._create_picking(picking_type="in", confirm=True)
        cls.picking_in_done = cls._create_picking(picking_type="in", confirm=True)
        cls._picking_action_done(cls.picking_in_done)
        # Create some outgoing pickings
        cls.picking_out_draft = cls._create_picking(picking_type="out")
        cls.picking_out_confirm = cls._create_picking(picking_type="out", confirm=True)
        cls.picking_out_done = cls._create_picking(picking_type="out", confirm=True)
        cls.picking_out_unavailable = cls._create_picking(
            picking_type="out", quantity=500.0, confirm=True
        )
        cls._picking_action_done(cls.picking_out_done)

    @classmethod
    def _create_picking(
        cls, picking_type="out", product=None, quantity=1.0, confirm=False
    ):
        assert picking_type in ("in", "out")
        if product is None:
            product = cls.product
        vals = {
            "partner_id": cls.partner.id,
            "picking_type_id": getattr(cls, f"picking_type_{picking_type}").id,
        }
        if picking_type == "out":
            vals.update(
                {
                    "location_id": cls.location_stock.id,
                    "location_dest_id": cls.location_customers.id,
                }
            )
        else:
            vals.update(
                {
                    "location_id": cls.location_suppliers.id,
                    "location_dest_id": cls.location_stock.id,
                }
            )
        vals["move_lines"] = [
            Command.create(
                {
                    "name": product.display_name,
                    "product_id": product.id,
                    "product_uom": product.uom_id.id,
                    "product_uom_qty": quantity,
                    "location_id": vals["location_id"],
                    "location_dest_id": vals["location_dest_id"],
                }
            ),
        ]
        picking = cls.env["stock.picking"].create(vals)
        if confirm:
            picking.action_confirm()
        return picking

    @classmethod
    def _picking_action_done(cls, picking):
        for move in picking.move_lines:
            move.quantity_done = move.product_uom_qty
        return picking._action_done()

    def test_search_is_set(self):
        pickings = self.env["stock.picking"].search(
            [
                ("move_lines.product_id", "=", self.product.id),
                ("products_availability_state", "!=", False),
            ]
        )
        self.assertEqual(
            pickings,
            self.picking_out_confirm + self.picking_out_unavailable,
        )

    def test_search_is_not_set(self):
        pickings = self.env["stock.picking"].search(
            [
                ("move_lines.product_id", "=", self.product.id),
                ("products_availability_state", "=", False),
            ]
        )
        self.assertEqual(
            pickings,
            self.picking_in_draft
            + self.picking_in_confirm
            + self.picking_in_done
            + self.picking_out_draft
            + self.picking_out_done,
        )

    def test_search_is_available(self):
        pickings = self.env["stock.picking"].search(
            [
                ("move_lines.product_id", "=", self.product.id),
                ("products_availability_state", "=", "available"),
            ]
        )
        self.assertEqual(pickings, self.picking_out_confirm)

    def test_search_is_not_available(self):
        pickings = self.env["stock.picking"].search(
            [
                ("move_lines.product_id", "=", self.product.id),
                ("products_availability_state", "!=", "available"),
            ]
        )
        self.assertEqual(
            pickings,
            self.picking_in_confirm
            + self.picking_in_draft
            + self.picking_in_done
            + self.picking_out_draft
            + self.picking_out_done
            + self.picking_out_unavailable,
        )
