# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestStockOverrideProcurement(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("product.product_product_8")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.output_location = cls.env.ref("stock.stock_location_output")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.picking_type_internal = cls.env.ref("stock.picking_type_internal")
        cls.procurement_group = cls.env["procurement.group"].create(
            {"name": "procurement group"}
        )
        routes = cls.env["stock.route"].create(
            [
                {
                    "name": "route 1 for product",
                    "product_selectable": True,
                    "sequence": 1,
                    "rule_ids": [
                        Command.create(
                            {
                                "name": "Stock -> output rule",
                                "action": "pull",
                                "picking_type_id": cls.picking_type_out.id,
                                "location_src_id": cls.stock_location.id,
                                "location_dest_id": cls.customer_location.id,
                            },
                        )
                    ],
                },
                {
                    "name": "route 2 for product",
                    "product_selectable": True,
                    "sequence": 1,
                    "rule_ids": [
                        Command.create(
                            {
                                "name": "Stock -> output rule",
                                "action": "pull",
                                "picking_type_id": cls.picking_type_internal.id,
                                "location_src_id": cls.stock_location.id,
                                "location_dest_id": cls.output_location.id,
                            },
                        )
                    ],
                },
            ]
        )
        cls.product.write({"route_ids": [Command.set(routes.ids)]})

    def _run_procurement(self, values):
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product,
                    1,
                    self.product.uom_id,
                    self.customer_location,
                    "procurement",
                    "procurement",
                    self.customer_location.company_id,
                    values,
                )
            ]
        )

    def test_normal_procurement(self):
        self._run_procurement({"group_id": self.procurement_group})
        picking = self.env["stock.picking"].search(
            [("group_id", "=", self.procurement_group.id)]
        )
        self.assertEqual(picking.location_dest_id, self.customer_location)
        self.assertEqual(picking.move_ids.product_uom_qty, 1)

    def test_override_procurement_location(self):
        self._run_procurement(
            {
                "group_id": self.procurement_group,
                "location_id": self.output_location,
            }
        )
        picking = self.env["stock.picking"].search(
            [("group_id", "=", self.procurement_group.id)]
        )
        self.assertEqual(picking.location_dest_id, self.output_location)

    def test_override_procurement_qty(self):
        self._run_procurement(
            {
                "group_id": self.procurement_group,
                "product_qty": 2,
            }
        )
        picking = self.env["stock.picking"].search(
            [("group_id", "=", self.procurement_group.id)]
        )
        self.assertEqual(picking.move_ids.product_uom_qty, 2)
