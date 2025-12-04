# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.addons.base.tests.common import BaseCommon


class TestNextPicking(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Change routes to trigger moves:
        # Suppliers -> Input -> Stock
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.suppliers = cls.env.ref("stock.stock_location_suppliers")
        cls.warehouse.reception_steps = "two_steps"
        pull = cls.warehouse.reception_route_id.rule_ids.filtered(
            lambda r: r.action == "pull"
        )
        push = cls.warehouse.reception_route_id.rule_ids.filtered(
            lambda r: r.action == "push"
        )
        # purchase_stock is maybe installed
        if len(cls.warehouse.reception_route_id.rule_ids) < 2:
            cls.env["stock.rule"].create(
                {
                    "name": "Suppliers -> Input",
                    "action": "pull",
                    "location_dest_id": cls.warehouse.wh_input_stock_loc_id.id,
                    "location_src_id": cls.suppliers.id,
                    "procure_method": "make_to_stock",
                    "route_id": cls.warehouse.reception_route_id.id,
                    "picking_type_id": cls.warehouse.in_type_id.id,
                }
            )
            push.action = "pull"
        else:
            pull.location_src_id = cls.suppliers
            pull.location_dest_id = cls.warehouse.wh_input_stock_loc_id
            push.action = "pull"
        cls.warehouse.reception_route_id.product_selectable = True

        cls.product = cls.env["product.product"].create({"name": "Test Product"})
        cls.product.route_ids = cls.warehouse.reception_route_id
        cls.suppliers = cls.env.ref("stock.stock_location_suppliers")

    def test_next_picking(self):
        # Create a procurement on Stock
        # Check the first move has the next picking name
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product,
                    1.0,
                    self.product.uom_id,
                    self.warehouse.lot_stock_id,
                    "test_mtso",
                    "test_mtso",
                    self.warehouse.company_id,
                    {
                        "warehouse_id": self.warehouse,
                    },
                ),
            ]
        )
        moves = self.env["stock.move"].search(
            [
                ("location_id", "=", self.suppliers.id),
                ("product_id", "=", self.product.id),
            ]
        )
        self.assertTrue(moves)
        self.assertTrue(moves.next_picking_ids)
        self.assertTrue(moves.next_picking_name)

        name = moves.move_dest_ids.picking_id.name

        self.assertEqual(name, moves.next_picking_name)
