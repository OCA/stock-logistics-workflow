# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class StockPickingCase(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(StockPickingCase, self).setUp(*args, **kwargs)
        obj_location = self.env["stock.location"]
        loc_view_1 = self.env.ref(
            "stock.warehouse0").view_location_id
        self.loc_transit_1 = obj_location.create({
            "name": "Transit Pull",
            "usage": "transit",
            "location_id": loc_view_1.id,
            })
        self.product1 = self.env["product.product"].create({
            "name": "Product Example",
            })
        route = self.env[
            "stock.location.route"].create({
                "name": "Inter-Warehouse Pull",
                "product_selectable": True,
                })
        self.env[
            "procurement.rule"].create({
                "name": "Pull from Main WH",
                "route_id": route.id,
                "location_id": self.loc_transit_1.id,
                "location_src_id": self.env.ref(
                    "stock.warehouse0").lot_stock_id.id,
                "procure_method": "make_to_order",
                "action": "move",
                "picking_type_id": self.env.ref(
                    "stock.warehouse0").int_type_id.id,
                })

    def test_1(self):
        picking = self.env[
            "stock.picking"].create({
                "picking_type_id": self.env.ref(
                    "stock.warehouse0").int_type_id.id,
                "create_procurement_group": False,
                })
        self.env["stock.move"].create({
            "name": self.product1.name,
            "product_id": self.product1.id,
            "picking_id": picking.id,
            "product_uom_qty": 10.0,
            "product_uom": self.product1.uom_id.id,
            "procure_method": "make_to_order",
            "location_id": self.loc_transit_1.id,
            "location_dest_id": self.env.ref(
                "stock.stock_warehouse_shop0").lot_stock_id.id,
            })
        picking.action_confirm()
        self.assertFalse(picking.group_id)
        picking2 = picking.copy()
        picking2.create_procurement_group = True
        picking2.action_confirm()
        self.assertTrue(picking2.group_id)
