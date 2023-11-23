# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.stock_quant_package_dimension.tests import common


class TestStockQuantPackageWeight(common.TestStockQuantPackageCommon):
    def test_package_estimated_pack_weight_kg(self):
        self.env["stock.quant"]._update_available_quantity(
            self.product,
            self.wh.out_type_id.default_location_src_id,
            7.0,
            package_id=self.package,
        )
        # 1 Box + 2 Small Box to satisfy 7 qties => 11kg
        self.assertEqual(self.package.estimated_pack_weight_kg, 11)
        self.move._action_assign()
        for line in self.move.move_line_ids:
            line.qty_done = line.reserved_uom_qty
        self.assertEqual(
            self.package.with_context(
                picking_id=self.move.picking_id.id
            ).estimated_pack_weight_kg,
            11,
        )
