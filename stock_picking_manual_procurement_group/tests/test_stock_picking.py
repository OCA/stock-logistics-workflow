# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class StockPickingCase(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(StockPickingCase, self).setUp(*args, **kwargs)
        obj_location = self.env["stock.location"]
        self.obj_procurement = self.env["procurement.order"]
        loc_view_1 = self.env.ref(
            "stock.warehouse0").view_location_id
        self.loc_transit_1 = obj_location.create({
            "name": "Transit Pull",
            "usage": "transit",
            "location_id": loc_view_1.id,
            })
        self.product1 = self.env["product.product"].create({
            "name": "X Product Example 1",
            })
        self.product2 = self.env["product.product"].create({
            "name": "X Product Example 2",
            })
        route = self.env[
            "stock.location.route"].create({
                "name": "Inter-Warehouse Pull",
                "product_selectable": True,
                })
        self.rule = self.env[
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

    def _create_picking(self, create_procurement_group=False):
        res_picking = {
            "picking_type_id": self.env.ref(
                "stock.warehouse0").int_type_id.id,
            "create_procurement_group": create_procurement_group,
            }

        picking = self.env[
            "stock.picking"].create(res_picking)

        res_move_1 = {
            "name": self.product1.name,
            "product_id": self.product1.id,
            "picking_id": picking.id,
            "product_uom_qty": 10.0,
            "product_uom": self.product1.uom_id.id,
            "procure_method": "make_to_order",
            "location_id": self.loc_transit_1.id,
            "location_dest_id": self.env.ref(
                "stock.stock_warehouse_shop0").lot_stock_id.id,
            }

        self.env["stock.move"].create(res_move_1)

        res_move_2 = {
            "name": self.product2.name,
            "product_id": self.product2.id,
            "picking_id": picking.id,
            "product_uom_qty": 10.0,
            "product_uom": self.product1.uom_id.id,
            "procure_method": "make_to_order",
            "location_id": self.loc_transit_1.id,
            "location_dest_id": self.env.ref(
                "stock.stock_warehouse_shop0").lot_stock_id.id,
            }

        self.env["stock.move"].create(res_move_2)

        return picking

    def _check_move_group(self, picking):
        for move in picking.move_lines:
            self.assertEqual(
                move.group_id,
                picking.group_id)

    def _get_generated_procurements(self, picking):
        criteria = [
            ("group_id", "=", picking.group_id.id),
            ]
        return self.obj_procurement.search(criteria)

    def _run_procurements(self, procurements):
        for procurement in procurements:
            procurement.write(
                {"rule_id": self.rule.id})

            if procurement.state == "confirmed":
                procurement.run()

    def _get_new_moves(self, procurements):
        new_moves = []
        for procurement in procurements:
            new_moves += procurement.move_ids

        return new_moves

    def test_1(self):
        picking = self._create_picking()
        picking.action_confirm()
        self.assertFalse(picking.group_id)

    def test_2(self):
        picking2 = self._create_picking(True)
        picking2.action_confirm()
        self.assertTrue(picking2.group_id)
        self._check_move_group(picking2)

        procurements = self._get_generated_procurements(
            picking2)
        self.assertEqual(
            len(procurements),
            2)

        self._run_procurements(procurements)

        new_moves = self._get_new_moves(procurements)

        for new_move in new_moves:
            self.assertEqual(
                new_move.group_id,
                picking2.group_id)

            self.assertEqual(
                new_move.picking_id.group_id,
                picking2.group_id)

    def test_3(self):
        picking1 = self._create_picking(True)
        picking2 = self._create_picking(True)

        picking1.action_confirm()
        picking2.action_confirm()

        group1 = picking1.group_id
        group2 = picking2.group_id

        self.assertNotEqual(
            group1,
            group2)

        procurements1 = self._get_generated_procurements(
            picking1)
        procurements2 = self._get_generated_procurements(
            picking2)
        self._run_procurements(
            procurements1 + procurements2)

        new_moves1 = self._get_new_moves(procurements1)
        new_picking1 = False
        for new_move1 in new_moves1:
            if not new_picking1:
                new_picking1 = new_move1.picking_id
            self.assertEqual(
                new_move1.group_id,
                group1)

            self.assertEqual(
                new_move1.picking_id.group_id,
                group1)

            self.assertEqual(
                new_move1.picking_id,
                new_picking1)

        new_moves2 = self._get_new_moves(procurements2)
        new_picking2 = False
        for new_move2 in new_moves2:
            if not new_picking2:
                new_picking2 = new_move2.picking_id
            self.assertEqual(
                new_move2.group_id,
                group2)

            self.assertEqual(
                new_move2.picking_id.group_id,
                group2)

            self.assertEqual(
                new_move2.picking_id,
                new_picking2)

        self.assertNotEqual(
            new_picking1,
            new_picking2)
