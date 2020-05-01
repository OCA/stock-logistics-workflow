# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import SavepointCase


class TestPickingTypeShippingPolicyGroupBy(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.pick_type = cls.warehouse.pick_type_id
        cls.pick_type.group_pickings = True
        cls.product = cls.env.ref("product.product_product_9")
        cls.group = cls.env["procurement.group"].create(
            {"name": "Test 1", "move_type": "direct"}
        )

    def _create_single_move(self, picking_type, group, product):
        move_vals = {
            "name": product.name,
            "picking_type_id": picking_type.id,
            "product_id": product.id,
            "product_uom_qty": 1.0,
            "product_uom": product.uom_id.id,
            "location_id": picking_type.default_location_src_id.id,
            "location_dest_id": picking_type.default_location_dest_id.id,
            "state": "confirmed",
            "procure_method": "make_to_stock",
            "group_id": group.id,
        }
        return self.env["stock.move"].create(move_vals)

    def test_shipping_policy_force_picking_type_one(self):
        """When the picking type changes move_type to 'one'

        If the picking type creates a stock.picking for move1 with move_type
        'one', ensure that the method that assign move2 to a new picking search
        using the same move_type.
        """
        self.group.move_type = "direct"
        self.pick_type.shipping_policy = "force_all_products_ready"
        move1 = self._create_single_move(self.pick_type, self.group, self.product)
        move1._assign_picking()
        move2 = self._create_single_move(self.pick_type, self.group, self.product)
        move2._assign_picking()
        self.assertEqual(move1.picking_id, move2.picking_id)
        self.assertEqual(move1.picking_id.move_type, "one")
