# Copyright 2026 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestRestrictPartner(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product1 = self.env["product.product"].create(
            {
                "name": "Test",
                "type": "consu",
                "is_storable": True,
            }
        )
        self.product2 = self.env["product.product"].create(
            {
                "name": "Test",
                "type": "consu",
                "is_storable": True,
            }
        )
        self.partner = self.env["res.partner"].create({"name": "Partner"})
        self.owner = self.env["res.partner"].create({"name": "Owner"})
        self.warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )
        self.warehouse.delivery_steps = "pick_ship"

    def test_restrict_partner(self):
        warehouse = self.warehouse
        final_location = self.partner.property_stock_customer
        self.env["stock.quant"]._update_available_quantity(
            self.product1, warehouse.lot_stock_id, 10.0, owner_id=self.owner
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product2, warehouse.lot_stock_id, 10.0, owner_id=self.owner
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product2, warehouse.lot_stock_id, 10.0
        )

        group = self.env["procurement.group"].create({"name": "1"})
        self.env["procurement.group"].run(
            [
                group.Procurement(
                    self.product1,
                    10,
                    self.product1.uom_id,
                    final_location,
                    "1",
                    "1",
                    warehouse.company_id,
                    {
                        "warehouse_id": warehouse,
                        "group_id": group,
                        "restrict_partner_id": self.owner.id,
                    },
                ),
                group.Procurement(
                    self.product2,
                    10,
                    self.product2.uom_id,
                    final_location,
                    "1",
                    "1",
                    warehouse.company_id,
                    {
                        "warehouse_id": warehouse,
                        "group_id": group,
                        "restrict_partner_id": self.owner.id,
                    },
                ),
                group.Procurement(
                    self.product2,
                    10,
                    self.product2.uom_id,
                    final_location,
                    "1",
                    "1",
                    warehouse.company_id,
                    {
                        "warehouse_id": warehouse,
                        "group_id": group,
                    },
                ),
            ]
        )

        all_pickings = self.env["stock.picking"].search([("group_id", "=", group.id)])
        pickings = all_pickings.filtered(lambda picking: picking.owner_id)
        pickings_without_owner = all_pickings - pickings
        self.assertEqual(pickings_without_owner.move_ids.product_id, self.product2)
        self.assertEqual(pickings.move_ids.product_id, (self.product1 | self.product2))
        # The procurement only creates the pick, the ship is pushed on validation
        pick = pickings
        self.assertEqual(pick.picking_type_id, warehouse.pick_type_id)
        pick.action_assign()
        self.assertEqual(pick.owner_id, self.owner)
        self.assertEqual(pick.move_ids.restrict_partner_id, self.owner)
        self.assertEqual(pick.move_line_ids.owner_id, self.owner)
        pick.move_ids.picked = True
        pick.button_validate()
        ship = pick.move_ids.move_dest_ids.picking_id
        self.assertEqual(ship.picking_type_id, warehouse.out_type_id)
        self.assertEqual(ship.owner_id, self.owner)
        self.assertEqual(ship.move_ids.restrict_partner_id, self.owner)
        self.assertEqual(ship.move_line_ids.owner_id, self.owner)

    def test_restrict_partner_pull(self):
        warehouse = self.warehouse
        final_location = self.partner.property_stock_customer
        output_location = warehouse.wh_output_stock_loc_id
        route = self.env["stock.route"].create(
            {
                "name": "Pull pick ship",
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Output to customer",
                            "action": "pull",
                            "procure_method": "make_to_order",
                            "location_src_id": output_location.id,
                            "location_dest_id": final_location.id,
                            "picking_type_id": warehouse.out_type_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Stock to output",
                            "action": "pull",
                            "procure_method": "make_to_stock",
                            "location_src_id": warehouse.lot_stock_id.id,
                            "location_dest_id": output_location.id,
                            "picking_type_id": warehouse.pick_type_id.id,
                        },
                    ),
                ],
            }
        )
        group = self.env["procurement.group"].create({"name": "1"})
        self.env["procurement.group"].run(
            [
                group.Procurement(
                    self.product1,
                    10,
                    self.product1.uom_id,
                    final_location,
                    "1",
                    "1",
                    warehouse.company_id,
                    {
                        "warehouse_id": warehouse,
                        "group_id": group,
                        "route_ids": route,
                        "restrict_partner_id": self.owner.id,
                    },
                ),
            ]
        )
        pickings = self.env["stock.picking"].search([("group_id", "=", group.id)])
        pick = pickings.filtered(
            lambda picking: picking.picking_type_id == warehouse.pick_type_id
        )
        ship = pickings - pick
        self.assertEqual(len(pick), 1)
        self.assertEqual(ship.picking_type_id, warehouse.out_type_id)
        self.assertEqual(pick.move_ids.move_dest_ids, ship.move_ids)
        for picking in pick | ship:
            self.assertEqual(picking.owner_id, self.owner)
            self.assertEqual(picking.move_ids.restrict_partner_id, self.owner)
