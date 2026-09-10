# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestStockLandedCost(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.StockPickingType = cls.env["stock.picking.type"]
        cls.StockLocation = cls.env["stock.location"]
        cls.StockPicking = cls.env["stock.picking"]
        cls.category_fifo = cls.env["product.category"].create(
            {
                "name": "Landed Cost FIFO",
                "property_cost_method": "fifo",
            }
        )
        cls.category_average = cls.env["product.category"].create(
            {
                "name": "Landed Cost Average",
                "property_cost_method": "average",
            }
        )
        cls.product_category_fifo = cls.env["product.product"].create(
            {
                "name": "Product Landed Cost FIFO",
                "categ_id": cls.category_fifo.id,
                "standard_price": 50,
                "detailed_type": "product",
            }
        )
        cls.product_category_average = cls.env["product.product"].create(
            {
                "name": "Product Landed Cost average ",
                "categ_id": cls.category_average.id,
                "standard_price": 60,
                "detailed_type": "product",
            }
        )
        cls.stock_picking_type = cls.StockPickingType.create(
            {
                "name": "Test picking type",
                "sequence_code": "TEST",
            }
        )
        cls.stock_location_internal = cls.StockLocation.create(
            {
                "name": "Test location internal",
                "usage": "internal",
                "barcode": "8411322222111",
            }
        )

        picking_id = cls.StockPicking.create(
            {
                "picking_type_id": cls.stock_picking_type.id,
                "move_ids_without_package": [
                    Command.create(
                        {
                            "name": cls.product_category_fifo.name,
                            "product_id": cls.product_category_fifo.id,
                            "product_uom_qty": 10,
                            "quantity": 10,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "location_id": cls.stock_location_internal.id,
                            "location_dest_id": cls.stock_location_internal.id,
                        }
                    ),
                    Command.create(
                        {
                            "name": cls.product_category_average.name,
                            "product_id": cls.product_category_average.id,
                            "product_uom_qty": 20,
                            "quantity": 20,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "location_id": cls.stock_location_internal.id,
                            "location_dest_id": cls.stock_location_internal.id,
                        }
                    ),
                ],
            }
        )

        cls.account_id = cls.env["account.account"].create(
            {
                "name": "Test asset current",
                "code": "TEST",
                "account_type": "asset_current",
            }
        )

        cls.landed_cost_id = cls.env["stock.landed.cost"].create(
            {
                "company_id": cls.env.company.id,
                "state": "draft",
                "picking_ids": picking_id.ids,
                "cost_lines": [
                    Command.create(
                        {
                            "product_id": cls.product_category_fifo.id,
                            "name": "Product Landed Cost FIFO",
                            "account_id": cls.account_id.id,
                            "price_unit": 50,
                            "split_method": "equal",
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_category_average.id,
                            "name": "Product Landed Cost average",
                            "account_id": cls.account_id.id,
                            "price_unit": 60,
                            "split_method": "equal",
                        }
                    ),
                ],
            }
        )

    def test_landed_cost_revert(self):
        self.landed_cost_id.button_validate()
        self.assertEqual(self.landed_cost_id.state, "done")
        self.landed_cost_id.revert_landed_costs()
        self.assertEqual(self.landed_cost_id.revert_landed_cost_count, 1)
        self.assertEqual(len(self.landed_cost_id.revert_landed_cost_ids), 1)
        revert = self.landed_cost_id.revert_landed_cost_ids
        self.assertEqual(revert.state, "draft")
        self.assertEqual(revert.landed_cost_id, self.landed_cost_id)
        self.assertEqual(revert.picking_ids, self.landed_cost_id.picking_ids)
        self.assertEqual(revert.vendor_bill_id, self.landed_cost_id.vendor_bill_id)

    def test_revert_cost_lines_are_negated(self):
        self.landed_cost_id.button_validate()
        self.landed_cost_id.revert_landed_costs()
        revert_lines = self.landed_cost_id.revert_landed_cost_ids.cost_lines
        self.assertEqual(len(revert_lines), len(self.landed_cost_id.cost_lines))
        revert_lines_by_product = {line.product_id: line for line in revert_lines}
        for line in self.landed_cost_id.cost_lines:
            revert_line = revert_lines_by_product[line.product_id]
            self.assertEqual(revert_line.price_unit, -line.price_unit)
            self.assertEqual(revert_line.name, line.name)
            self.assertEqual(revert_line.account_id, line.account_id)
            self.assertEqual(revert_line.split_method, line.split_method)

    def test_revert_returns_action_on_new_landed_cost(self):
        self.landed_cost_id.button_validate()
        action = self.landed_cost_id.revert_landed_costs()
        revert = self.landed_cost_id.revert_landed_cost_ids
        self.assertEqual(action["res_model"], "stock.landed.cost")
        self.assertEqual(action["domain"], [("id", "=", revert.id)])

    def test_action_view_revert_landed_cost(self):
        self.landed_cost_id.button_validate()
        self.landed_cost_id.revert_landed_costs()
        action = self.landed_cost_id.action_view_revert_landed_cost()
        self.assertEqual(action["res_model"], "stock.landed.cost")
        self.assertEqual(
            action["domain"],
            [("id", "in", self.landed_cost_id.revert_landed_cost_ids.ids)],
        )

    def test_revert_requires_single_record(self):
        other_landed_cost = self.landed_cost_id.copy(
            {"picking_ids": self.landed_cost_id.picking_ids.ids}
        )
        landed_costs = self.landed_cost_id + other_landed_cost
        landed_costs.button_validate()
        with self.assertRaises(ValueError):
            landed_costs.revert_landed_costs()
        with self.assertRaises(ValueError):
            landed_costs.action_view_revert_landed_cost()
