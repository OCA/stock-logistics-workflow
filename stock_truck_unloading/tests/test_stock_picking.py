from datetime import datetime

from odoo.tests.common import TransactionCase


class TestStockPicking(TransactionCase):
    def setUp(self):
        super(TestStockPicking, self).setUp()
        self.product = self.env.ref("product.product_product_4")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.location = self.warehouse.lot_stock_id
        self.dest_location = self.env.ref("stock.stock_location_customers")
        self.outgoing_picking_type = self.env.ref("stock.picking_type_out")
        self.incoming_picking_type = self.env.ref("stock.picking_type_in")

    def _create_picking(self):
        self.picking_data = {
            "picking_type_id": self.outgoing_picking_type.id,
            "move_type": "direct",
            "location_id": self.location.id,
            "location_dest_id": self.dest_location.id,
            "manage_truck_arrival": True,
        }

        self.picking = self.env["stock.picking"].create(self.picking_data)

        self.move_data = {
            "picking_id": self.picking.id,
            "product_id": self.product.id,
            "location_id": self.location.id,
            "location_dest_id": self.dest_location.id,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date_deadline": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": self.product.name,
            "procure_method": "make_to_stock",
            "product_uom": self.product.uom_id.id,
            "product_uom_qty": 1.0,
        }

        self.env["stock.move"].create(self.move_data)

        return self.picking

    def test_confirm_picking_no_error(self):
        picking = self._create_picking()
        picking.action_confirm()
        self.assertEqual(self.picking.state, "confirmed")

    def test_confirm_picking_no_error_with_truck_arrived(self):
        picking = self._create_picking()
        picking.do_truck_arrived()
        picking.action_confirm()
        self.assertEqual(self.picking.state, "confirmed")

    def test_confirm_picking_date_truck_arrival_if_truck_arrived(self):
        picking_with_truck = self._create_picking()
        picking_without_truck = self._create_picking()

        picking_with_truck.action_confirm()
        picking_with_truck.do_truck_arrived()

        picking_without_truck.action_confirm()

        self.assertEqual(
            picking_with_truck.date_truck_arrival.replace(
                minute=0, second=0, microsecond=0
            ),
            datetime.now().replace(minute=0, second=0, microsecond=0),
        )
        self.assertEqual(picking_without_truck.date_truck_arrival, False)
