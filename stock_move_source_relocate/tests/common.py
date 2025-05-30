# Copyright 2020 Camptocamp (https://www.camptocamp.com)

from odoo.tests import common


class SourceRelocateCommon(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_delta = cls.env.ref("base.res_partner_4")
        cls.wh = cls.env["stock.warehouse"].create(
            {
                "name": "Base Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "WHTEST",
            }
        )
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")

        cls.loc_shelf = cls.env["stock.location"].create(
            {"name": "Shelves", "location_id": cls.wh.lot_stock_id.id}
        )
        cls.loc_shelf_1 = cls.env["stock.location"].create(
            {"name": "Shelf 1", "location_id": cls.loc_shelf.id}
        )
        cls.loc_shelf_2 = cls.env["stock.location"].create(
            {"name": "Shelf 2", "location_id": cls.loc_shelf.id}
        )
        cls.loc_replenish = cls.env["stock.location"].create(
            {"name": "Replenish", "location_id": cls.loc_shelf.id}
        )

        cls.product = cls.env["product.product"].create(
            {"name": "Product", "type": "consu", "is_storable": True}
        )
        cls.product2 = cls.env["product.product"].create(
            {"name": "Product2", "type": "consu", "is_storable": True}
        )

    def _create_single_move(self, product, picking_type):
        move_vals = {
            "name": product.name,
            "picking_type_id": picking_type.id,
            "product_id": product.id,
            "product_uom_qty": 10.0,
            "product_uom": product.uom_id.id,
            "location_id": picking_type.default_location_src_id.id,
            "location_dest_id": picking_type.default_location_dest_id.id,
            "state": "confirmed",
            "procure_method": "make_to_stock",
        }
        return self.env["stock.move"].create(move_vals)

    def _create_relocate_rule(self, location, relocation, picking_type, domain=None):
        self.env["stock.source.relocate"].create(
            {
                "location_id": location.id,
                "picking_type_id": picking_type.id,
                "relocate_location_id": relocation.id,
                "rule_domain": domain or "[]",
            }
        )

    def _update_qty_in_location(self, location, product, quantity):
        self.env["stock.quant"]._update_available_quantity(product, location, quantity)
