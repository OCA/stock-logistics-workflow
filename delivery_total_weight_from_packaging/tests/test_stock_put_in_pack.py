# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command

from .common import TestShippingWeightCommon


class TestPutInPackWeight(TestShippingWeightCommon):
    def _get_wiz(self, picking):
        return self.env["stock.put.in.pack"].create(
            {"move_line_ids": [Command.set(picking.move_line_ids.ids)]}
        )

    def _assign_picking(self, qty):
        self.move.product_uom_qty = qty
        self.env["stock.quant"]._update_available_quantity(
            self.product,
            self.wh.out_type_id.default_location_src_id,
            qty * 2,
        )
        picking = self.move.picking_id
        picking.action_assign()
        picking.move_ids.picked = True
        return picking

    def test_put_in_pack_shipping_weight1(self):
        # 12 units => 2 Box (7) + 2 Small Box (2)
        picking = self._assign_picking(12)
        wiz = self._get_wiz(picking)
        self.assertEqual(wiz.shipping_weight, 18)

    def test_put_in_pack_shipping_weight2(self):
        # 15 units => 3 Box (7)
        picking = self._assign_picking(15)
        wiz = self._get_wiz(picking)
        self.assertEqual(wiz.shipping_weight, 21)
