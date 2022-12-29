# Copyright 2022 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import SavepointCase


class TestStockMoveForcedLot(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.StockMove = cls.env["stock.move"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.location1 = cls.env.ref("stock.stock_location_stock")
        cls.location2 = cls.env.ref("stock.stock_location_components")
        cls.picking_type = cls.env.ref("stock.picking_type_internal")
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        route_auto = cls.env["stock.location.route"].create(
            {"name": "Auto Create Group"}
        )
        cls.rule_1 = cls.env["stock.rule"].create(
            {
                "name": "rule with autocreate",
                "route_id": route_auto.id,
                "action": "pull_push",
                "warehouse_id": cls.warehouse.id,
                "picking_type_id": cls.picking_type.id,
                "location_id": cls.location1.id,
                "location_src_id": cls.location2.id,
                "partner_address_id": cls.partner.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product 1",
                "type": "product",
                "tracking": "serial",
                "route_ids": [(6, 0, [route_auto.id])],
            }
        )

    def test_01_create_procurement_with_fixed_lot(self):
        nb_product_todo = 5
        serials = []
        for i in range(nb_product_todo):
            serials.append(
                self.env["stock.production.lot"].create(
                    {
                        "name": f"lot_consumed_{i}",
                        "product_id": self.product.id,
                        "company_id": self.env.company.id,
                    }
                )
            )
            self.env["stock.quant"]._update_available_quantity(
                self.product, self.location2, 1, lot_id=serials[-1]
            )
        move = self.StockMove.search([("product_id", "=", self.product.id)])
        self.assertFalse(move)
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product,
                    1.0,
                    self.product.uom_id,
                    self.location1,
                    "Test",
                    "Odoo test",
                    self.env.company,
                    {
                        "lot_id": serials[3].id,
                    },
                )
            ]
        )
        move = self.StockMove.search([("product_id", "=", self.product.id)])
        self.assertTrue(move)
        self.assertEqual(move.forced_lot_id, serials[3])
        move._action_assign()
        self.assertEqual(move.move_line_ids.lot_id, serials[3])
