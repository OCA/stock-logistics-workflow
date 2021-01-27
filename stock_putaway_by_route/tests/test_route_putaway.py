# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import Form, SavepointCase


class TestRoutePutaway(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.input_location = cls.env.ref("stock.stock_location_company")
        cls.input_gate_a_location = cls.env.ref("stock.location_gate_a")
        cls.shelf_location = cls.env.ref("stock.stock_location_components")

        cls.product = cls.env["product.product"].create(
            {"name": "Product", "type": "product"}
        )

        cls.route = cls.env["stock.location.route"].create(
            {
                "name": "Transfer",
                "product_categ_selectable": False,
                "product_selectable": True,
                "company_id": cls.env.ref("base.main_company").id,
                "sequence": 10,
            }
        )
        cls.rule = cls.env["stock.rule"].create(
            {
                "name": "Transfer",
                "route_id": cls.route.id,
                "location_src_id": cls.input_location.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "action": "pull",
                "picking_type_id": cls.warehouse.int_type_id.id,
                "procure_method": "make_to_stock",
                "warehouse_id": cls.warehouse.id,
                "company_id": cls.env.ref("base.main_company").id,
            }
        )
        cls.env["stock.putaway.rule"].create(
            {
                "route_id": cls.route.id,
                "location_in_id": cls.warehouse.lot_stock_id.id,
                "location_out_id": cls.shelf_location.id,
            }
        )

    def _create_single_move(self, product, rule=None):
        picking_type = self.warehouse.int_type_id
        move_vals = {
            "name": product.name,
            "picking_type_id": picking_type.id,
            "product_id": product.id,
            "product_uom_qty": 2.0,
            "product_uom": product.uom_id.id,
            "location_id": self.input_location.id,
            "location_dest_id": picking_type.default_location_dest_id.id,
            "state": "confirmed",
            "procure_method": "make_to_stock",
            "rule_id": rule.id if rule else None,
        }
        return self.env["stock.move"].create(move_vals)

    def _update_product_qty_in_location(self, location, product, quantity):
        self.env["stock.quant"]._update_available_quantity(product, location, quantity)

    def test_route_putaway_move_route(self):
        move = self._create_single_move(self.product, rule=self.rule)
        self._update_product_qty_in_location(
            self.input_gate_a_location, self.product, move.product_uom_qty
        )
        move._assign_picking()
        move._action_assign()
        self.assertEqual(move.move_line_ids.location_dest_id, self.shelf_location)

    def test_route_putaway_product(self):
        self.product.route_ids = self.route
        move = self._create_single_move(self.product)
        self._update_product_qty_in_location(
            self.input_gate_a_location, self.product, move.product_uom_qty
        )
        move._assign_picking()
        move._action_assign()
        self.assertEqual(move.move_line_ids.location_dest_id, self.shelf_location)

    def test_route_putaway_onchange_move_line(self):
        # the group is necessary to have the put-away rule applied on
        # StockMoveLine.onchange_product_id
        self.env.user.groups_id |= self.env.ref("stock.group_stock_multi_locations")

        picking_type = self.warehouse.int_type_id
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": self.input_location.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
            }
        )

        # the onchange is applied on move line only for NewID records
        # otherwise we are not even allowed to change the product
        view_move_line = Form(self.env["stock.move.line"])
        view_move_line.picking_id = picking
        view_move_line.location_id = self.input_location
        view_move_line.location_dest_id = picking.location_dest_id
        view_move_line.product_id = self.product

        self.assertEqual(view_move_line.location_dest_id, picking.location_dest_id)

        # trigger StockMoveLine.onchange_product_id
        route_product = self.env["product.product"].create(
            {"name": "Product with route", "type": "product"}
        )
        route_product.route_ids |= self.route
        view_move_line.product_id = route_product

        self.assertEqual(view_move_line.location_dest_id, self.shelf_location)
