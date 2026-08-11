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
        self.assertEqual(self.landed_cost_id.revert_landed_cost_ids[0].state, "draft")
