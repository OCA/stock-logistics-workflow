# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import TransactionCase


class TestPickingTypeShippingPolicy(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.warehouse = cls.env.ref("stock.warehouse0")
        # set pick-pack-ship on warehouse
        cls.warehouse.delivery_steps = "pick_pack_ship"
        cls.pick_type = cls.warehouse.pick_type_id
        cls.pack_type = cls.warehouse.pack_type_id
        cls.ship_type = cls.warehouse.out_type_id

        cls.customers_location = cls.env.ref("stock.stock_location_customers")
        cls.output_location = cls.warehouse.wh_output_stock_loc_id

        cls.product = cls.env.ref("product.product_product_9")
        # Create ir.default for procure_method as make_to_order in order to
        #  generate chained moves
        cls.env["ir.default"].create(
            {
                "field_id": cls.env.ref("stock.field_stock_move__procure_method").id,
                "json_value": '"make_to_order"',
            }
        )

    def test_shipping_policy(self):
        self.pack_type.shipping_policy = "force_all_products_ready"
        self.pick_type.shipping_policy = "force_as_soon_as_possible"
        # Create picking
        out_picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.ship_type.id,
                "location_id": self.output_location.id,
                "location_dest_id": self.customers_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 10.0,
                            "product_uom": self.product.uom_id.id,
                            "location_id": self.output_location.id,
                            "location_dest_id": self.customers_location.id,
                        },
                    )
                ],
            }
        )
        out_picking.action_confirm()

        pack_picking = out_picking.move_ids.move_orig_ids.picking_id
        pick_picking = pack_picking.move_ids.move_orig_ids.picking_id
        self.assertEqual(pack_picking.picking_type_id, self.pack_type)
        self.assertEqual(pack_picking.move_type, "one")
        self.assertEqual(pick_picking.picking_type_id, self.pick_type)
        self.assertEqual(pick_picking.move_type, "direct")
