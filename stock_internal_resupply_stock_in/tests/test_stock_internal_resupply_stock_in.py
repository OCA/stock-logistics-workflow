# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestStockInternalResupplyStockIn(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env["res.config.settings"].write(
            {
                "group_stock_adv_location": True,
                "group_stock_multi_locations": True,
            }
        )
        cls.product = cls.env.ref("product.product_product_4")
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.wh2 = cls.env["stock.warehouse"].create({"name": "WH2", "code": "WH2"})
        cls.wh2.reception_steps = "two_steps"
        cls.wh2.resupply_wh_ids = cls.wh.ids

        cls.int_supply_route = cls.env["stock.location.route"].search(
            [("supplier_wh_id", "=", cls.wh.id), ("supplied_wh_id", "=", cls.wh2.id)]
        )
        cls.product.product_tmpl_id.route_ids = [(4, cls.int_supply_route.id)]
        cls.picking = cls.create_picking(cls.wh2.stock_in_type_id.id)
        cls.picking.action_confirm()

    @classmethod
    def create_picking(cls, picking_type):
        picking = cls.env["stock.picking"].create(
            {
                "location_id": cls.wh2.wh_input_stock_loc_id.id,
                "location_dest_id": cls.wh2.lot_stock_id.id,
                "picking_type_id": picking_type,
                "immediate_transfer": False,
            }
        )
        cls.env["stock.move.line"].create(
            {
                "product_id": cls.product.id,
                "product_uom_id": cls.product.uom_id.id,
                "qty_done": 10,
                "location_id": cls.wh2.wh_input_stock_loc_id.id,
                "location_dest_id": cls.wh2.lot_stock_id.id,
                "picking_id": picking.id,
            }
        )
        return picking

    def test_action_confirm(self):
        self.assertEqual(self.picking.move_lines.procure_method, "make_to_order")
        picking2 = self.create_picking(self.wh2.in_type_id.id)
        self.assertNotEqual(picking2.move_lines.procure_method, "make_to_order")

    def test_count_picking_stock_in(self):
        self.assertEqual(self.wh.out_type_id.count_picking_stock_in, 1)

    def test_check_resupply_and_steps(self):
        with self.assertRaises(ValidationError):
            self.wh.resupply_wh_ids = self.wh2.ids
