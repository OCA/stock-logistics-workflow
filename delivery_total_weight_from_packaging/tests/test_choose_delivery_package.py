# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestShippingWeightCommon


class TestDeliveryPackageWeight(TestShippingWeightCommon):
    def _get_wiz(self, picking, packaging=None):
        # `default_picking_id` is required for default weight compute
        wiz = (
            self.env["choose.delivery.package"]
            .with_context(default_picking_id=picking.id)
            .create({"delivery_packaging_id": packaging.id if packaging else None})
        )
        return wiz

    def test_picking_shipping_weight1(self):
        # "Small Box", "qty": "1", "max_weight": "2"
        # "Box", "qty": "5", "max_weight": "7"
        self.move.product_uom_qty = 12
        self.env["stock.quant"]._update_available_quantity(
            self.product,
            self.wh.out_type_id.default_location_src_id,
            self.move.product_uom_qty * 2,
        )
        picking = self.move.picking_id
        picking.action_assign()
        for line in picking.move_line_ids:
            line.qty_done = line.product_qty

        wiz = self._get_wiz(picking)
        self.assertEqual(wiz.shipping_weight, 18)

    def test_picking_shipping_weight2(self):
        # "Small Box", "qty": "1", "max_weight": "2"
        # "Box", "qty": "5", "max_weight": "7"
        self.move.product_uom_qty = 15
        self.env["stock.quant"]._update_available_quantity(
            self.product,
            self.wh.out_type_id.default_location_src_id,
            self.move.product_uom_qty * 2,
        )
        picking = self.move.picking_id
        picking.action_assign()
        for line in picking.move_line_ids:
            line.qty_done = line.product_qty

        wiz = self._get_wiz(picking)
        self.assertEqual(wiz.shipping_weight, 21)
