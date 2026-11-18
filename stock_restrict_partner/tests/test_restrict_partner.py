# Copyright 2026 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestRestrictPartner(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product1 = self.env["product.product"].create(
            {
                "name": "Test",
                "type": "product",
            }
        )
        self.product2 = self.env["product.product"].create(
            {
                "name": "Test",
                "type": "product",
            }
        )
        self.partner = self.env["res.partner"].create({"name": "Partner"})
        self.owner = self.env["res.partner"].create({"name": "Owner"})

    def test_restrict_partner(self):
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )
        warehouse.delivery_steps = "pick_ship"
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
        self.assertEqual(pickings_without_owner.move_lines.product_id, self.product2)
        self.assertEqual(
            pickings.move_lines.product_id, (self.product1 | self.product2)
        )
        pickings.action_assign()
        pick = pickings[1]
        ship = pickings[0]
        self.assertEqual(pick.owner_id, self.owner)
        self.assertEqual(pick.move_lines.restrict_partner_id, self.owner)
        self.assertEqual(pick.move_line_ids.owner_id, self.owner)
        pick.move_line_ids.qty_done = 10
        pick.button_validate()
        self.assertEqual(ship.owner_id, self.owner)
        self.assertEqual(ship.move_lines.restrict_partner_id, self.owner)
        self.assertEqual(ship.move_line_ids.owner_id, self.owner)
