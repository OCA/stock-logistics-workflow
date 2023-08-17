#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import first

from .common import TestCommon


class TestInventory(TestCommon):
    def test_inventory_yesterday(self):
        yesterday = self._get_datetime_backdating(1)
        product = first(self.products)
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Test backdating",
                "date_backdating": yesterday,
                "filter": "product",
                "product_id": product.id,
            }
        )
        inventory.action_start()
        inventory.line_ids.product_qty = 100
        inventory.action_validate()
        self.assertEqual(inventory.state, "done")

        stock_moves = inventory.move_ids
        self._check_stock_moves(stock_moves)
