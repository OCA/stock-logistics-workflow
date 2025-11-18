# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.fields import Command

from odoo.addons.stock_picking_batch_creation.tests.common import (
    ClusterPickingCommonFeatures,
)


class TestClusteringConditions(ClusterPickingCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = cls.env["procurement.group"].create(
            {
                "name": "Group Test",
            }
        )
        cls.type_group = cls.env["stock.picking.type.group"].create(
            {
                "name": "PICK group",
            }
        )
        cls.type_group.picking_type_ids |= cls.pick3.picking_type_id
        # Ensure there is always bins
        cls.make_picking_batch.stock_device_type_ids.nbr_bins = 10
        # Assign group to all pickings
        cls.picks.move_ids.group_id = cls.group
        cls.picks._compute_type_group_reservation_rate()

    def test_picking_with_reservation_rate_range_no_picking(self):
        self.make_picking_batch.group_reservation_rate = True
        self.make_picking_batch.group_reservation_rate_max = 90.0
        batch = self.make_picking_batch._create_batch()
        self.assertFalse(batch.picking_ids)

    def test_picking_with_reservation_rate_range(self):
        self.make_picking_batch.group_reservation_rate = True
        batch = self.make_picking_batch._create_batch()
        self.assertEqual((self.pick1 | self.pick2 | self.pick3), batch.picking_ids)

    def test_picking_with_reservation_rate_range_constrains(self):
        self.make_picking_batch.group_reservation_rate = True
        with self.assertRaises(ValidationError):
            self.make_picking_batch.group_reservation_rate_max = 110.0

        with self.assertRaises(ValidationError):
            self.make_picking_batch.group_reservation_rate_max = -110.0

        with self.assertRaises(ValidationError):
            self.make_picking_batch.group_reservation_rate_min = -110.0

        self.make_picking_batch.group_reservation_rate_max = 90.0
        with self.assertRaises(ValidationError):
            self.make_picking_batch.group_reservation_rate_min = 100.0

    def test_picking_with_additional_reservation_rate_range_constrains(self):
        self.make_picking_batch.additional_group_reservation_rate = True
        with self.assertRaises(ValidationError):
            self.make_picking_batch.additional_group_reservation_rate_max = 110.0

        with self.assertRaises(ValidationError):
            self.make_picking_batch.additional_group_reservation_rate_max = -110.0

        with self.assertRaises(ValidationError):
            self.make_picking_batch.additional_group_reservation_rate_min = -110.0

        self.make_picking_batch.additional_group_reservation_rate_max = 90.0
        with self.assertRaises(ValidationError):
            self.make_picking_batch.additional_group_reservation_rate_min = 100.0

    def test_picking_with_additional_reservation_rate_range(self):
        procurement_group = self.env["procurement.group"].create(
            {
                "name": "Test",
            }
        )
        values = {"group_id": procurement_group}
        self.warehouse_1.pick_type_id.picking_type_group_id = self.type_group
        picks_before = self.env["stock.move"].search(
            [
                ("location_dest_id", "=", self.warehouse_1.wh_output_stock_loc_id.id),
                ("product_id", "=", self.p1.id),
            ]
        )
        picks_before._action_cancel()
        self.env["stock.picking.type.group"].create(
            {
                "name": "OUTS",
                "picking_type_ids": [Command.set(self.warehouse_1.out_type_id.ids)],
            }
        )
        self.warehouse_1.delivery_steps = "pick_ship"
        self.warehouse_1.delivery_route_id.rule_ids.filtered(
            lambda rule: rule.location_src_id
            == self.env.ref("stock.stock_location_stock")
        ).write(
            {
                "location_dest_id": self.warehouse_1.wh_output_stock_loc_id.id,
            }
        )
        self.warehouse_1.delivery_route_id.rule_ids.filtered(
            lambda rule: rule.location_src_id == self.warehouse_1.wh_output_stock_loc_id
        ).write(
            {
                "action": "pull",
            }
        )
        self.warehouse_1.out_type_id.additional_picking_type_group_id = self.type_group
        self.p1.route_ids |= self.warehouse_1.delivery_route_id
        self.location_customers = self.env.ref("stock.stock_location_customers")
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.p1,
                    20.0,
                    self.p1.uom_id,
                    self.location_customers,
                    self.p1.name,
                    "/",
                    self.env.company,
                    values,
                )
            ]
        )
        move_out = self.env["stock.move"].search(
            [
                ("location_dest_id", "=", self.location_customers.id),
                ("product_id", "=", self.p1.id),
            ]
        )
        move_pick = self.env["stock.move"].search(
            [
                ("location_dest_id", "=", self.warehouse_1.wh_output_stock_loc_id.id),
                ("state", "!=", "cancel"),
                ("product_id", "=", self.p1.id),
            ]
        )
        self.make_picking_batch.additional_group_reservation_rate = True
        self.make_picking_batch.picking_type_ids = self.warehouse_1.out_type_id

        move_pick.move_line_ids.picked = True
        move_pick.picking_id._action_done()

        batch = self.make_picking_batch._create_batch()
        self.assertIn(move_out.picking_id, batch.picking_ids)

        batch.action_cancel()

        self.make_picking_batch.additional_group_reservation_rate_min = 60.0
        batch = self.make_picking_batch._create_batch()
        self.assertNotIn(move_out.picking_id, batch.picking_ids)
