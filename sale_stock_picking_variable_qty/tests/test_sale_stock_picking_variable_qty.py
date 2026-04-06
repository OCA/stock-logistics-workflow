# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import Command
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestSaleStockPickingVariableQty(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Variable Qty Product",
                "is_storable": True,
                "invoice_policy": "delivery",
            }
        )
        cls.warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Warehouse Pick Ship",
                "code": "VQP",
                "delivery_steps": "pick_ship",
            }
        )
        delivery_route = cls.warehouse.delivery_route_id
        delivery_route.rule_ids[0].write(
            {"location_dest_id": delivery_route.rule_ids[1].location_src_id.id}
        )
        delivery_route.rule_ids[1].write({"action": "pull"})
        cls.warehouse.pick_type_id.sale_stock_picking_variable_qty = True
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.warehouse.lot_stock_id, 20.0
        )

    @classmethod
    def _create_sale_order(cls, quantity, product=None):
        product = product or cls.product
        return cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "warehouse_id": cls.warehouse.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": quantity,
                        }
                    )
                ],
            }
        )

    def _confirm_sale_and_get_pickings(self, ordered_qty, product=None):
        product = product or self.product
        order = self._create_sale_order(ordered_qty, product=product)
        order.action_confirm()
        self.assertEqual(len(order.picking_ids), 2)
        pick_picking = order.picking_ids.filtered(
            lambda p: p.location_dest_id == self.warehouse.wh_output_stock_loc_id
        )
        ship_picking = order.picking_ids.filtered(
            lambda p: p.location_dest_id.usage == "customer"
        )
        self.assertEqual(len(pick_picking), 1)
        self.assertEqual(len(ship_picking), 1)
        return order, pick_picking, ship_picking

    def _process_pick(self, pick_picking, done_qty):
        pick_picking.action_assign()
        move = pick_picking.move_ids
        move.quantity = done_qty
        move.picked = True
        move._action_done()
        return move

    def _create_return(self, picking, qty):
        return_wiz_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.id,
                active_model="stock.picking",
            )
        )
        return_wiz = return_wiz_form.save()
        return_wiz.product_return_moves.quantity = qty
        res = return_wiz.action_create_returns()
        return self.env["stock.picking"].browse(res["res_id"])

    def _get_backorder(self, picking):
        return self.env["stock.picking"].search([("backorder_id", "=", picking.id)])

    def test_pick_partial_creates_backorder_without_changing_sale_line_qty(self):
        order, pick_picking, ship_picking = self._confirm_sale_and_get_pickings(10.0)
        sale_line = order.order_line.filtered(
            lambda line: line.product_id == self.product
        )
        self._process_pick(pick_picking, 6.0)
        backorder_pick = self._get_backorder(pick_picking)
        self.assertEqual(sale_line.product_uom_qty, 10.0)
        self.assertEqual(ship_picking.move_ids.quantity, 6.0)
        self.assertEqual(ship_picking.move_ids.product_uom_qty, 10.0)
        self.assertEqual(backorder_pick.move_ids.product_uom_qty, 4.0)

    def test_pick_extra_updates_sale_line_qty(self):
        order, pick_picking, ship_picking = self._confirm_sale_and_get_pickings(10.0)
        sale_line = order.order_line.filtered(
            lambda line: line.product_id == self.product
        )
        ship_move = ship_picking.move_ids.filtered(
            lambda move: move.product_id == self.product
        )
        self._process_pick(pick_picking, 12.0)
        self.assertEqual(sale_line.product_uom_qty, 12.0)
        self.assertEqual(ship_move.product_uom_qty, 12.0)

    def test_pick_keeps_sale_line_qty_when_disabled(self):
        self.warehouse.pick_type_id.sale_stock_picking_variable_qty = False
        order, pick_picking, ship_picking = self._confirm_sale_and_get_pickings(10.0)
        sale_line = order.order_line.filtered(
            lambda line: line.product_id == self.product
        )
        ship_move = ship_picking.move_ids.filtered(
            lambda move: move.product_id == self.product
        )
        self._process_pick(pick_picking, 6.0)
        self.assertEqual(sale_line.product_uom_qty, 10.0)
        self.assertEqual(ship_move.product_uom_qty, 10.0)

    def test_pick_partial_then_extra_backorder_updates_sale_line_qty(self):
        order, pick_picking, ship_picking = self._confirm_sale_and_get_pickings(10.0)
        sale_line = order.order_line.filtered(
            lambda line: line.product_id == self.product
        )
        self._process_pick(pick_picking, 6.0)
        backorder_pick = self._get_backorder(pick_picking)
        self.assertEqual(backorder_pick.move_ids.product_uom_qty, 4.0)
        self._process_pick(backorder_pick, 5.0)
        self.assertEqual(sale_line.product_uom_qty, 11.0)
        self.assertEqual(ship_picking.move_ids.product_uom_qty, 11.0)

    def test_return_keeps_sale_line_qty(self):
        order, pick_picking, ship_picking = self._confirm_sale_and_get_pickings(10.0)
        sale_line = order.order_line.filtered(
            lambda line: line.product_id == self.product
        )
        self._process_pick(pick_picking, 10.0)
        self._process_pick(ship_picking, 10.0)
        return_picking = self._create_return(ship_picking, 10.0)
        self.assertFalse(return_picking.picking_type_id.sale_stock_picking_variable_qty)
        self._process_pick(return_picking, 5.0)
        return_backorder = self.env["stock.picking"].search(
            [("backorder_id", "=", return_picking.id)]
        )
        self.assertEqual(sale_line.product_uom_qty, 10.0)
        self.assertEqual(return_picking.move_ids.quantity, 5.0)
        self.assertEqual(return_backorder.move_ids.product_uom_qty, 5.0)

    def test_pick_ignores_products_invoiced_on_order(self):
        order_product = self.env["product.product"].create(
            {
                "name": "Ordered Invoice Product",
                "is_storable": True,
                "invoice_policy": "order",
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            order_product, self.warehouse.lot_stock_id, 20.0
        )
        order, pick_picking, ship_picking = self._confirm_sale_and_get_pickings(
            10.0, product=order_product
        )
        sale_line = order.order_line.filtered(
            lambda line: line.product_id == order_product
        )
        ship_move = ship_picking.move_ids.filtered(
            lambda move: move.product_id == order_product
        )
        self._process_pick(pick_picking, 12.0)
        self.assertEqual(sale_line.product_uom_qty, 10.0)
        self.assertEqual(ship_move.product_uom_qty, 10.0)
