# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase


class TestStockPickingInterWarehouse(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Company = cls.env["res.company"]
        cls.Partner = cls.env["res.partner"]
        cls.Product = cls.env["product.product"]
        cls.StockMove = cls.env["stock.move"]
        cls.StockWarehouse = cls.env["stock.warehouse"]
        cls.StockLocation = cls.env["stock.location"]
        cls.StockPicking = cls.env["stock.picking"]
        cls.StockPickingType = cls.env["stock.picking.type"]
        cls.StockLocationRoute = cls.env["stock.location.route"]

        # Testing with a new company to make sure everything is created
        # correctly even in multi company scenarios
        cls.test_company = cls.Company.create({"name": "Test Company"})
        cls.test_partner_1 = cls.Partner.create({"name": "WH1 Partner"})
        cls.test_partner_2 = cls.Partner.create({"name": "WH2 Partner"})

        cls.stock_wh1 = cls.StockWarehouse.search(
            [("company_id", "=", cls.test_company.id)]
        )
        cls.stock_wh2 = cls.StockWarehouse.create(
            {
                "partner_id": cls.test_company.partner_id.id,
                "name": "WH2 Test",
                "code": "WH2T",
                "company_id": cls.test_company.id,
            }
        )

        cls.product_oven = cls.Product.create(
            {
                "name": "Microwave Oven",
                "type": "product",
                "standard_price": 1.0,
                "weight": 20,
                "volume": 1.5,
            }
        )
        cls.product_refrigerator = cls.Product.create(
            {
                "name": "Refrigerator",
                "type": "product",
                "standard_price": 1.0,
                "weight": 10,
                "volume": 1,
            }
        )

        # setup warehouses
        cls.stock_wh1.write(
            {
                "inter_warehouse_transfers": True,
                "receipt_destination_location_id": cls.stock_wh1.view_location_id.id,
                "receipt_picking_type_id": cls.stock_wh1.in_type_id.id,
                "receipt_picking_partner_id": cls.test_partner_1.id,
            }
        )

        cls.stock_wh2.write(
            {
                "inter_warehouse_transfers": True,
                "receipt_destination_location_id": cls.stock_wh2.view_location_id.id,
                "receipt_picking_type_id": cls.stock_wh2.in_type_id.id,
                "receipt_picking_partner_id": cls.test_partner_2.id,
            }
        )

    def test_create_route_for_companies(self):
        for company in self.Company.search([]):
            self.assertTrue(company.inter_warehouse_route_id)

    def test_configure_warehouse_for_intercompany(self):
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
        route_inter_wh_id = self.test_company.inter_warehouse_route_id
        self.assertTrue(route_inter_wh_id)
        self.assertFalse(route_inter_wh_id.product_selectable)
        self.assertFalse(route_inter_wh_id.product_categ_selectable)
        self.assertTrue(route_inter_wh_id.warehouse_selectable)
        self.assertIn(self.stock_wh1, route_inter_wh_id.warehouse_ids)

        # The route must have a rule set
        rule_id = route_inter_wh_id.rule_ids[0]
        self.assertTrue(rule_id)
        self.assertEqual(rule_id.action, "push")
        self.assertEqual(
            rule_id.picking_type_id, self.stock_wh1.receipt_picking_type_id
        )
        self.assertEqual(rule_id.location_src_id, location_id)
        self.assertEqual(rule_id.location_id, self.stock_wh1.view_location_id)
        self.assertEqual(rule_id.company_id, self.stock_wh1.company_id)
        self.assertEqual(rule_id.route_id, route_inter_wh_id)

        # Editing the warehouse will edit the related rule
        # without creating a new one
        self.stock_wh1.write(
            {"receipt_destination_location_id": self.stock_wh2.view_location_id.id}
        )
        self.assertEqual(len(route_inter_wh_id.rule_ids), 2)
        self.assertEqual(rule_id.location_id, self.stock_wh2.view_location_id)

        # Setting another warehouse as inter-warehouse
        # must add to the same route
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
        self.assertEqual(new_rule_id.location_id, self.stock_wh2.view_location_id)
        self.assertEqual(new_rule_id.company_id, self.stock_wh2.company_id)
        self.assertEqual(new_rule_id.route_id, route_inter_wh_id)

        # Remove the first warehouse
        self.stock_wh1.write({"inter_warehouse_transfers": False})
        self.assertEqual(route_inter_wh_id.warehouse_ids.ids, self.stock_wh2.ids)
        self.assertEqual(len(route_inter_wh_id.rule_ids), 1)

    def test_wh_unique_picking_partner(self):
        self.stock_wh1.receipt_picking_partner_id = self.test_company.partner_id
        with self.assertRaises(ValidationError):
            self.stock_wh2.receipt_picking_partner_id = self.test_company.partner_id

    def test_picking_create(self):
        self.stock_wh1.int_type_id.write(
            {
                "inter_warehouse_transfer": True,
                "disable_merge_picking_moves": True,
            }
        )

        picking_out = self.StockPicking.create(
            {
                "picking_type_id": self.stock_wh1.int_type_id.id,
                "location_id": self.stock_wh1.int_type_id.default_location_src_id.id,
                "location_dest_id": self.stock_wh1.int_type_id.default_location_dest_id.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": self.product_oven.name,
                            "product_id": self.product_oven.id,
                            "product_uom_qty": 3,
                            "product_uom": self.product_oven.uom_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.product_refrigerator.name,
                            "product_id": self.product_refrigerator.id,
                            "product_uom_qty": 3,
                            "product_uom": self.product_refrigerator.uom_id.id,
                        },
                    ),
                ],
            }
        )
        # test that onchange_picking_type() uses the right
        # destination location instead of the picking type's default destination location
        picking_out.write({"partner_id": self.test_partner_2.id})
        picking_out.onchange_picking_type()
        self.assertEqual(
            self.test_partner_2.default_stock_location_src_id,
            picking_out.location_dest_id,
        )

        for ml in picking_out.move_lines:
            ml.quantity_done = 3
        for ml in picking_out.move_lines.move_line_ids:
            ml.qty_done = 3

        picking_out.button_validate()

        # There should be two moves
        # in the same picking
        move_in = self.StockMove.search(
            [("inter_warehouse_picking_id", "=", picking_out.id)]
        )
        self.assertEqual(len(move_in), 2)
        picking_in = move_in.picking_id
        self.assertEqual(len(picking_in), 1)
        self.assertEqual(len(picking_out.move_lines), len(picking_in.move_lines))
