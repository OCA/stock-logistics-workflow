from odoo.addons.stock_move_source_relocate.tests.test_source_relocate import (
    SourceRelocateCommon,
)


class TestSourceRelocate(SourceRelocateCommon):
    def test_relocate_with_routing(self):
        """Check that routing is applied when a relocation happen"""
        # Relocation: for unavailable move in Stock, relocate to Replenish
        self._create_relocate_rule(
            self.wh.lot_stock_id, self.loc_replenish, self.wh.pick_type_id
        )
        # Routing: a move with source location in replenishment is classified
        # in picking type Replenish
        pick_type_replenish = self.env["stock.picking.type"].create(
            {
                "name": "Replenish",
                "code": "internal",
                "sequence_code": "R",
                "warehouse_id": self.wh.id,
                "use_create_lots": False,
                "use_existing_lots": True,
                "default_location_src_id": self.loc_replenish.id,
                "default_location_dest_id": self.wh.lot_stock_id.id,
            }
        )
        self.env["stock.routing"].create(
            {
                "location_id": self.loc_replenish.id,
                "picking_type_id": self.wh.pick_type_id.id,
                "rule_ids": [
                    (
                        0,
                        0,
                        {"method": "pull", "picking_type_id": pick_type_replenish.id},
                    )
                ],
            }
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
                    # routing changed the picking type
                    "picking_type_id": pick_type_replenish.id,
                    "location_id": self.loc_replenish.id,
                }
            ],
        )
        # routing created a new move
        self.assertTrue(move.move_dest_ids)
