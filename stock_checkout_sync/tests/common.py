# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import SavepointCase


class CheckoutSyncCommonCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.packing_location = cls.env.ref("stock.location_pack_zone")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write({"delivery_steps": "pick_pack_ship"})
        cls.stock_shelf_location = cls.env.ref("stock.stock_location_components")
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Product", "type": "product"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Product2", "type": "product"}
        )
        cls.pick_type = cls.warehouse.pick_type_id
        cls.pack_type = cls.warehouse.pack_type_id
        cls.procurement_group_1 = cls.env["procurement.group"].create(
            {"name": "Test 1"}
        )

    @classmethod
    def _update_qty_in_location(cls, location, product, quantity):
        cls.env["stock.quant"]._update_available_quantity(product, location, quantity)

    @classmethod
    def _create_single_move(cls, picking_type, product, move_orig=None):
        move_vals = {
            "name": product.name,
            "picking_type_id": picking_type.id,
            "product_id": product.id,
            "product_uom_qty": 2.0,
            "product_uom": product.uom_id.id,
            "location_id": picking_type.default_location_src_id.id,
            "location_dest_id": picking_type.default_location_dest_id.id,
            "state": "confirmed",
            "procure_method": "make_to_stock",
            "group_id": cls.procurement_group_1.id,
        }
        if move_orig:
            move_vals.update(
                {
                    "procure_method": "make_to_order",
                    "state": "waiting",
                    "move_orig_ids": [(6, 0, move_orig.ids)],
                }
            )
        return cls.env["stock.move"].create(move_vals)

    def assert_locations(self, expected):
        for moves, location in expected.items():
            for move in moves:
                self.assertEqual(move.location_dest_id, location)
                for line in move.move_line_ids:
                    self.assertEqual(line.location_dest_id, location)
                for dest in move.move_dest_ids:
                    self.assertEqual(dest.location_id, location)
