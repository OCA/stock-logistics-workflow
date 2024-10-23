# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase

from .common import ZoneLocationSourceCommon


class TestPickingZoneSource(ZoneLocationSourceCommon, TransactionCase):
    def test_flow(self):
        self._create_customer_need()
        self.env["procurement.group"].run_scheduler()
        self.picking_out = self.Picking.search(
            [
                ("move_ids.product_id", "in", self.products.ids),
                ("picking_type_id", "=", self.warehouse.out_type_id.id),
            ]
        )
        pharma_move = self.picking_out.move_ids.filtered(
            lambda move: move.product_id == self.pharma_product
        )
        food_move = self.picking_out.move_ids.filtered(
            lambda move: move.product_id == self.food_product
        )
        normal_move = self.picking_out.move_ids.filtered(
            lambda move: move.product_id == self.normal_product
        )
        self.assertTrue(pharma_move)
        self.assertTrue(food_move)

        self.assertEqual(pharma_move.source_zone_location_ids, self.pharma_location)
        self.assertEqual(food_move.source_zone_location_ids, self.food_location)
        self.assertEqual(
            normal_move.source_zone_location_ids, self.warehouse.lot_stock_id
        )
