# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class MoveSourceReassignCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.delivery_steps = "pick_ship"
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
            }
        )
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "product",
            }
        )
        cls.shop_out = cls.env["stock.location"].create(
            {
                "name": "Shop OUT",
                "location_id": cls.warehouse.view_location_id.id,
            }
        )
        cls.picking_type_stock_shop = cls.env["stock.picking.type"].create(
            {
                "name": "Pick Shop",
                "sequence_code": "P-SHOP/",
                "default_location_dest_id": cls.shop_out.id,
                "default_location_src_id": cls.warehouse.lot_stock_id.id,
            }
        )
        cls.picking_type_delivery_shop = cls.env["stock.picking.type"].create(
            {
                "name": "Delivery Shop",
                "sequence_code": "D-SHOP/",
                "default_location_dest_id": cls.customers.id,
                "default_location_src_id": cls.shop_out.id,
            }
        )
        cls.picking_type_transfer = cls.env["stock.picking.type"].create(
            {
                "name": "Transfer Shop -> OUT",
                "sequence_code": "TRANS/",
                "default_location_dest_id": cls.warehouse.wh_output_stock_loc_id.id,
                "default_location_src_id": cls.shop_out.id,
            }
        )
        cls.route_shop = cls.env["stock.route"].create(
            {
                "name": "Shop Delivery",
                "rule_ids": [
                    Command.create(
                        {
                            "name": "Stock -> Shop",
                            "action": "pull",
                            "picking_type_id": cls.picking_type_stock_shop.id,
                            "procure_method": "make_to_stock",
                            "location_dest_id": cls.shop_out.id,
                            "location_src_id": cls.warehouse.lot_stock_id.id,
                            "warehouse_id": cls.warehouse.id,
                        }
                    ),
                    Command.create(
                        {
                            "name": "Shop -> Customers",
                            "action": "pull",
                            "picking_type_id": cls.picking_type_delivery_shop.id,
                            "procure_method": "make_to_order",
                            "location_dest_id": cls.customers.id,
                            "location_src_id": cls.shop_out.id,
                            "warehouse_id": cls.warehouse.id,
                        }
                    ),
                ],
            }
        )
        cls.output = cls.warehouse.wh_output_stock_loc_id

        cls.output_1 = cls.env["stock.location"].create(
            {
                "name": "OUT 1",
                "location_id": cls.output.id,
            }
        )
        cls.output_2 = cls.env["stock.location"].create(
            {
                "name": "OUT 1",
                "location_id": cls.output.id,
            }
        )

        cls.env["stock.quant"].with_context(inventory_mode=True,).create(
            {
                "location_id": cls.warehouse.lot_stock_id.id,
                "inventory_quantity": 50.0,
                "product_id": cls.product_a.id,
            }
        )._apply_inventory()
        cls.env["stock.quant"].with_context(inventory_mode=True,).create(
            {
                "location_id": cls.warehouse.lot_stock_id.id,
                "inventory_quantity": 50.0,
                "product_id": cls.product_b.id,
            }
        )._apply_inventory()

    def _create_needs(self, delivery_only=False):
        self.product_a.route_ids |= self.warehouse.delivery_route_id
        self.product_b.route_ids |= self.warehouse.delivery_route_id
        proc_vals = {}
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_a,
                    5.0,
                    self.product_a.uom_id,
                    self.customers,
                    "Test 1",
                    "Test 1",
                    self.env.company,
                    proc_vals,
                ),
                self.env["procurement.group"].Procurement(
                    self.product_b,
                    5.0,
                    self.product_b.uom_id,
                    self.customers,
                    "Test 1",
                    "Test 1",
                    self.env.company,
                    proc_vals,
                ),
            ]
        )
        if delivery_only:
            return
        # Shop one
        proc_vals = {"route_ids": self.route_shop}
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_a,
                    5.0,
                    self.product_a.uom_id,
                    self.customers,
                    "Test 1",
                    "Test 1",
                    self.env.company,
                    proc_vals,
                ),
                self.env["procurement.group"].Procurement(
                    self.product_b,
                    5.0,
                    self.product_b.uom_id,
                    self.customers,
                    "Test 1",
                    "Test 1",
                    self.env.company,
                    proc_vals,
                ),
            ]
        )
