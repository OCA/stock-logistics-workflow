# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestCancelPicking(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.location_reserve = cls.env["stock.location"].create(
            {
                "name": "Reserve",
                "location_id": cls.warehouse.view_location_id.id,
            }
        )
        cls.picking_type_replenish = cls.env["stock.picking.type"].create(
            {
                "name": "Replenish",
                "default_location_dest_id": cls.warehouse.lot_stock_id.id,
                "default_location_src_id": cls.location_reserve.id,
                "sequence_code": "REPL",
                "cancel_waiting_picking_with_scheduler": True,
            }
        )
        cls.route = cls.env["stock.route"].create(
            {
                "name": "Replenish",
                "rule_ids": [
                    Command.create(
                        {
                            "name": "Replenish",
                            "action": "pull",
                            "picking_type_id": cls.picking_type_replenish.id,
                            "location_dest_id": cls.warehouse.lot_stock_id.id,
                            "location_src_id": cls.location_reserve.id,
                        }
                    )
                ],
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "is_storable": True,
            }
        )

        cls.orderpoint = cls.env["stock.warehouse.orderpoint"].create(
            {
                "location_id": cls.warehouse.lot_stock_id.id,
                "route_id": cls.route.id,
                "product_id": cls.product.id,
                "product_min_qty": 10.0,
                "product_max_qty": 20.0,
            }
        )

    def test_cancel_picking(self):
        self.env["procurement.group"].run_scheduler()
        pickings = self.env["stock.picking"].search(
            [("picking_type_id", "=", self.picking_type_replenish.id)]
        )
        self.assertTrue(pickings)
        self.env["procurement.group"].run_scheduler()
        self.assertEqual(pickings.state, "cancel")

    def test_no_cancel_picking(self):
        self.picking_type_replenish.cancel_waiting_picking_with_scheduler = False
        self.env["procurement.group"].run_scheduler()
        pickings = self.env["stock.picking"].search(
            [("picking_type_id", "=", self.picking_type_replenish.id)]
        )
        self.assertTrue(pickings)
        self.env["procurement.group"].run_scheduler()
        self.assertEqual(pickings.state, "confirmed")
