# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.addons.product_stock_default_putaway.tests.common import DefaultPutawayCommon


class StockMove(DefaultPutawayCommon):
    def test_move_default_putaway(self):
        self.move = self.env["stock.move"].create(
            {
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.stock_wh2.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 10.0,
                "name": self.product.name,
            }
        )
        self.assertEqual(self.stock_wh2_3, self.move.from_putaway_final_location_id)
