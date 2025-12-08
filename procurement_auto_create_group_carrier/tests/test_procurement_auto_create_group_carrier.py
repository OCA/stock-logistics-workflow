# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.base.tests.common import BaseCommon


class TestProcurementAutoCreateGroupCarrier(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.StockMove = cls.env["stock.move"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.location1 = cls.env.ref("stock.stock_location_stock")
        cls.location2 = cls.env.ref("stock.stock_location_components")
        cls.picking_type = cls.env.ref("stock.picking_type_internal")
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.carrier = cls.env.ref("delivery.free_delivery_carrier")
        cls.partner.property_delivery_carrier_id = cls.carrier
        route_auto = cls.env["stock.route"].create({"name": "Auto Create Group"})
        cls.rule_1 = cls.env["stock.rule"].create(
            {
                "name": "rule with autocreate",
                "route_id": route_auto.id,
                "auto_create_group": True,
                "action": "pull_push",
                "warehouse_id": cls.warehouse.id,
                "picking_type_id": cls.picking_type.id,
                "location_dest_id": cls.location1.id,
                "location_src_id": cls.location2.id,
                "partner_address_id": cls.partner.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product 1",
                "is_storable": True,
                "route_ids": [(6, 0, [route_auto.id])],
            }
        )

    def test_carrier_is_set_on_procurement_group(self):
        move = self.StockMove.search([("product_id", "=", self.product.id)])
        self.assertFalse(move)
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product,
                    5.0,
                    self.product.uom_id,
                    self.location1,
                    "Test",
                    "Odoo test",
                    self.env.company,
                    {},
                )
            ]
        )
        move = self.StockMove.search([("product_id", "=", self.product.id)])
        self.assertEqual(move.group_id.carrier_id, self.carrier)
