# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import Form

from odoo.addons.stock.tests.common import TestStockCommon


class TestConsumableMoveLocation(TestStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.consu_product = cls.env["product.product"].create(
            {"name": "Consumable", "type": "consu"}
        )
        cls.putaway_location = cls.env["stock.location"].create(
            {
                "name": "putaway loc for consumable",
                "usage": "internal",
                "location_id": cls.stock_location,
            }
        )
        cls.putaway = cls.env["stock.putaway.rule"].create(
            {
                "product_id": cls.consu_product.id,
                "location_in_id": cls.stock_location,
                "location_out_id": cls.putaway_location.id,
            }
        )

    def test_outgoing_move(self):
        move_form = Form(self.env["stock.move"])
        move_form.product_id = self.consu_product
        move_form.location_id = self.env["stock.location"].browse(self.stock_location)
        move_form.location_dest_id = self.env["stock.location"].browse(
            self.pack_location
        )
        move = move_form.save()
        self.assertEqual(move.state, "draft")
        self.assertEqual(move.location_id.id, self.stock_location)
        self.assertFalse(move.move_line_ids)
        move._action_confirm()
        self.assertEqual(move.state, "assigned")
        self.assertTrue(move.move_line_ids)
        self.assertEqual(move.move_line_ids.location_id, self.putaway_location)
