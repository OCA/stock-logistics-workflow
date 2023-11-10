# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestStockPickingInterWarehouse(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.StockWarehouse = cls.env["stock.warehouse"]
        cls.StockLocation = cls.env["stock.location"]
        cls.StockLocationRoute = cls.env["stock.location.route"]
        cls.StockPickingType = cls.env["stock.picking.type"]

        cls.stock_wh1 = cls.env.ref("stock.warehouse0")
        cls.stock_wh2 = cls.env.ref("stock_picking_inter_warehouse.stock_warehouse_wh2")

    def test_create_route(self):
        self.stock_wh1.write(
            {
                "inter_warehouse_transfers": True,
                "receipt_destination_location_id": self.stock_wh2.view_location_id.id,
                "receipt_picking_type_id": self.stock_wh2.in_type_id.id,
                "receipt_picking_partner_id": [(0, 0, {"name": "WH2"})],
            }
        )

        # Internal transit location should not be archived anymore
        company_internal_transit_location = (
            self.stock_wh1.company_id.internal_transit_location_id
        )
        self.assertTrue(company_internal_transit_location.active)

        # A new location must be created for this warehouse
        location_id = self.StockLocation.search(
            [
                ("name", "=", self.stock_wh1.name),
                ("location_id", "=", company_internal_transit_location.id),
            ]
        )
        self.assertTrue(location_id)

        # And a route as well
        route_inter_wh_id = self.env.ref(
            "stock_picking_inter_warehouse.stock_location_route_inter_warehouse"
        )
        self.assertTrue(route_inter_wh_id)
        self.assertFalse(route_inter_wh_id.product_selectable)
        self.assertFalse(route_inter_wh_id.product_categ_selectable)
        self.assertTrue(route_inter_wh_id.warehouse_selectable)
        self.assertIn(self.stock_wh1, route_inter_wh_id.warehouse_ids)

        # The route must have a rule set
        rule_id = route_inter_wh_id.rule_ids
        self.assertTrue(rule_id)
        self.assertEqual(rule_id.action, "push")
        self.assertEqual(
            rule_id.picking_type_id, self.stock_wh1.receipt_picking_type_id
        )
        self.assertEqual(rule_id.location_src_id, location_id)
        self.assertEqual(rule_id.location_id, self.stock_wh2.view_location_id)
        self.assertEqual(rule_id.company_id, self.stock_wh1.company_id)
        self.assertEqual(rule_id.route_id, route_inter_wh_id)

        # Editing the warehouse will edit the related rule
        # without creating a new one
        self.stock_wh1.write(
            {"receipt_destination_location_id": self.stock_wh1.view_location_id.id}
        )
        self.assertEqual(len(route_inter_wh_id.rule_ids), 1)
        self.assertEqual(rule_id.location_id, self.stock_wh1.view_location_id)

        # Setting another warehouse as inter-warehouse
        # must add to the same route
        self.stock_wh2.write(
            {
                "inter_warehouse_transfers": True,
                "receipt_destination_location_id": self.stock_wh1.view_location_id.id,
                "receipt_picking_type_id": self.stock_wh1.in_type_id.id,
                "receipt_picking_partner_id": self.stock_wh1.company_id.id,
            }
        )
        self.assertEqual(len(route_inter_wh_id.warehouse_ids), 2)
        self.assertIn(self.stock_wh2, route_inter_wh_id.warehouse_ids)

        location_id = self.StockLocation.search(
            [
                ("name", "=", self.stock_wh2.name),
                ("location_id", "=", company_internal_transit_location.id),
            ]
        )
        self.assertTrue(location_id)

        # And also create a new rule
        self.assertEqual(len(route_inter_wh_id.rule_ids), 2)
        new_rule_id = route_inter_wh_id.rule_ids.filtered(
            lambda x: self.stock_wh2.name in x.name
        )
        self.assertTrue(new_rule_id)
        self.assertEqual(new_rule_id.action, "push")
        self.assertEqual(
            new_rule_id.picking_type_id, self.stock_wh2.receipt_picking_type_id
        )
        self.assertEqual(new_rule_id.location_src_id, location_id)
        self.assertEqual(new_rule_id.location_id, self.stock_wh1.view_location_id)
        self.assertEqual(new_rule_id.company_id, self.stock_wh2.company_id)
        self.assertEqual(new_rule_id.route_id, route_inter_wh_id)

        # Remove the first warehouse
        self.stock_wh1.write({"inter_warehouse_transfers": False})
        self.assertEqual(route_inter_wh_id.warehouse_ids.ids, self.stock_wh2.ids)
        self.assertEqual(len(route_inter_wh_id.rule_ids), 1)
