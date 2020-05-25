# Copyright 2020 Camptocamp (https://www.camptocamp.com)

from odoo import exceptions
from odoo.tests import common


class SourceRelocateCommon(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_delta = cls.env.ref("base.res_partner_4")
        cls.wh = cls.env["stock.warehouse"].create(
            {
                "name": "Base Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "WHTEST",
            }
        )
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")

        cls.loc_shelf = cls.env["stock.location"].create(
            {"name": "Shelves", "location_id": cls.wh.lot_stock_id.id}
        )
        cls.loc_shelf_1 = cls.env["stock.location"].create(
            {"name": "Shelf 1", "location_id": cls.loc_shelf.id}
        )
        cls.loc_shelf_2 = cls.env["stock.location"].create(
            {"name": "Shelf 2", "location_id": cls.loc_shelf.id}
        )
        cls.loc_replenish = cls.env["stock.location"].create(
            {"name": "Replenish", "location_id": cls.loc_shelf.id}
        )

        cls.product = cls.env["product.product"].create(
            {"name": "Product", "type": "product"}
        )
        cls.product2 = cls.env["product.product"].create(
            {"name": "Product2", "type": "product"}
        )

    def _create_single_move(self, product, picking_type):
        move_vals = {
            "name": product.name,
            "picking_type_id": picking_type.id,
            "product_id": product.id,
            "product_uom_qty": 10.0,
            "product_uom": product.uom_id.id,
            "location_id": picking_type.default_location_src_id.id,
            "location_dest_id": picking_type.default_location_dest_id.id,
            "state": "confirmed",
            "procure_method": "make_to_stock",
        }
        return self.env["stock.move"].create(move_vals)

    def _create_relocate_rule(self, location, relocation, picking_type, domain=None):
        self.env["stock.source.relocate"].create(
            {
                "location_id": location.id,
                "picking_type_id": picking_type.id,
                "relocate_location_id": relocation.id,
                "rule_domain": domain or "[]",
            }
        )

    def _update_qty_in_location(self, location, product, quantity):
        self.env["stock.quant"]._update_available_quantity(product, location, quantity)


class TestSourceRelocate(SourceRelocateCommon):
    def test_relocate_child_of_location(self):
        # relocate location is a child, valid
        self.env["stock.source.relocate"].create(
            {
                "location_id": self.loc_shelf.id,
                "picking_type_id": self.wh.pick_type_id.id,
                "relocate_location_id": self.loc_replenish.id,
            }
        )

    def test_relocate_not_child_of_location(self):
        # relocate location must be a child
        with self.assertRaises(exceptions.ValidationError):
            self.env["stock.source.relocate"].create(
                {
                    "location_id": self.loc_shelf.id,
                    "picking_type_id": self.wh.pick_type_id.id,
                    "relocate_location_id": self.customer_loc.id,
                }
            )

    def test_relocate_whole_move(self):
        self._create_relocate_rule(
            self.wh.lot_stock_id, self.loc_replenish, self.wh.pick_type_id
        )
        move = self._create_single_move(self.product, self.wh.pick_type_id)
        move._assign_picking()
        move._action_assign()
        self.assertRecordValues(
            move,
            [
                {
                    "state": "confirmed",
                    "product_qty": 10.0,
                    "reserved_availability": 0.0,
                    "location_id": self.loc_replenish.id,
                }
            ],
        )

    def test_relocate_partial_move(self):
        self._create_relocate_rule(
            self.wh.lot_stock_id, self.loc_replenish, self.wh.pick_type_id
        )
        self._update_qty_in_location(self.loc_shelf_1, self.product, 3)
        move = self._create_single_move(self.product, self.wh.pick_type_id)
        move._assign_picking()
        move._action_assign()

        self.assertRecordValues(
            move,
            [
                {
                    "state": "assigned",
                    "product_qty": 3.0,
                    "reserved_availability": 3.0,
                    "location_id": self.wh.lot_stock_id.id,
                }
            ],
        )
        new_move = move.picking_id.move_lines - move
        self.assertRecordValues(
            new_move,
            [
                {
                    "state": "confirmed",
                    "product_qty": 7.0,
                    "reserved_availability": 0.0,
                    "location_id": self.loc_replenish.id,
                }
            ],
        )

    def test_relocate_ignore_available(self):
        self._create_relocate_rule(
            self.wh.lot_stock_id, self.loc_replenish, self.wh.pick_type_id
        )
        self._update_qty_in_location(self.loc_shelf_1, self.product, 10)
        move = self._create_single_move(self.product, self.wh.pick_type_id)
        move._assign_picking()
        move._action_assign()
        self.assertRecordValues(
            move,
            [
                {
                    "state": "assigned",
                    "product_qty": 10.0,
                    "reserved_availability": 10.0,
                    # keep the original location when it's available
                    "location_id": self.wh.lot_stock_id.id,
                }
            ],
        )

    def test_relocate_domain(self):
        self._create_relocate_rule(
            self.wh.lot_stock_id,
            self.loc_replenish,
            self.wh.pick_type_id,
            domain=[("product_id", "=", self.product.id)],
        )
        move = self._create_single_move(self.product, self.wh.pick_type_id)
        move2 = self._create_single_move(self.product2, self.wh.pick_type_id)
        moves = move + move2
        moves._assign_picking()
        moves._action_assign()
        self.assertRecordValues(
            move,
            [
                {
                    "state": "confirmed",
                    "product_qty": 10.0,
                    "reserved_availability": 0.0,
                    "location_id": self.loc_replenish.id,
                }
            ],
        )
        self.assertRecordValues(
            move2,
            [
                {
                    "state": "confirmed",
                    "product_qty": 10.0,
                    "reserved_availability": 0.0,
                    # the domain exclude this move from the relocation
                    "location_id": self.wh.lot_stock_id.id,
                }
            ],
        )

    def test_relocate_rule_picking_type(self):
        self._create_relocate_rule(
            self.wh.lot_stock_id, self.loc_replenish, self.wh.pick_type_id
        )
        move = self._create_single_move(self.product, self.wh.pick_type_id)
        move2 = self._create_single_move(self.product2, self.wh.int_type_id)
        move2.location_id = self.wh.lot_stock_id
        moves = move + move2
        moves._assign_picking()
        moves._action_assign()
        self.assertRecordValues(
            move,
            [
                {
                    "state": "confirmed",
                    "product_qty": 10.0,
                    "reserved_availability": 0.0,
                    "location_id": self.loc_replenish.id,
                }
            ],
        )
        self.assertRecordValues(
            move2,
            [
                {
                    "state": "confirmed",
                    "product_qty": 10.0,
                    "reserved_availability": 0.0,
                    # excluded by different picking type
                    "location_id": self.wh.lot_stock_id.id,
                }
            ],
        )

    def test_relocate_rule_location(self):
        self._create_relocate_rule(
            self.wh.lot_stock_id, self.loc_replenish, self.wh.pick_type_id
        )
        move = self._create_single_move(self.product, self.wh.pick_type_id)
        move2 = self._create_single_move(self.product2, self.wh.pick_type_id)
        move2.location_id = self.wh.wh_input_stock_loc_id
        moves = move + move2
        moves._assign_picking()
        moves._action_assign()
        self.assertRecordValues(
            move,
            [
                {
                    "state": "confirmed",
                    "product_qty": 10.0,
                    "reserved_availability": 0.0,
                    "location_id": self.loc_replenish.id,
                }
            ],
        )
        self.assertRecordValues(
            move2,
            [
                {
                    "state": "confirmed",
                    "product_qty": 10.0,
                    "reserved_availability": 0.0,
                    # excluded by different location
                    "location_id": self.wh.wh_input_stock_loc_id.id,
                }
            ],
        )
