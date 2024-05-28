from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase


class TestStockPickingPropagateScheduledDate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.output_location = cls.env.ref("stock.stock_location_output")
        cls.output_location.active = True
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

        # Configure a warehouse with delivery_steps = 'pick_ship'
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.delivery_steps = "pick_ship"

        # Create a product
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
            }
        )

        # Set initial stock
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.stock_location, 2.0
        )
        # Create a procurement for 3 Units of the product on the Customers location
        pg = cls.env["procurement.group"].create({"name": "Procurement"})
        cls.env["procurement.group"].run(
            [
                pg.Procurement(
                    cls.product,  # product_id
                    3.0,  # product_qty
                    cls.product.uom_id,  # product_uom
                    cls.customer_location,  # location_id
                    "procurement",  # name
                    "procurement",  # origin
                    cls.warehouse.company_id,  # company_id
                    # values
                    {"warehouse_id": cls.warehouse, "group_id": pg},
                )
            ]
        )
        # This will create 2 pickings: 1 for pick, 1 for ship
        cls.pick = cls.env["stock.picking"].search(
            [
                ("location_id", "=", cls.stock_location.id),
                ("location_dest_id", "=", cls.output_location.id),
                ("group_id", "=", pg.id),
            ]
        )
        cls.ship = cls.env["stock.picking"].search(
            [
                ("location_id", "=", cls.output_location.id),
                ("location_dest_id", "=", cls.customer_location.id),
                ("group_id", "=", pg.id),
            ]
        )

    def test_01_pick_reschedule(self):
        """change the Pick date"""
        # Set the scheduled_date of the Pick picking to next week.
        scheduled_date = datetime.now().replace(microsecond=0) + timedelta(days=7)
        self.pick.scheduled_date = scheduled_date

        delta = timedelta(seconds=2)
        # the date of the stock.move in the Pick picking is moved to next week
        self.assertAlmostEqual(
            self.pick.move_lines[0].date,
            scheduled_date,
            msg="The date of the stock.move in the Pick picking should be moved to next week",
            delta=delta,
        )
        # the date of the stock.move in the Ship picking is moved to next week
        self.assertAlmostEqual(
            self.ship.move_lines[0].date,
            scheduled_date,
            msg="The date of the stock.move in the Ship picking should be moved to next week",
            delta=delta,
        )

        # the scheduled_date of the Ship picking is moved to next week
        self.assertAlmostEqual(
            self.ship.scheduled_date,
            scheduled_date,
            msg="The `scheduled_date` of the Ship picking should be moved to next week",
            delta=delta,
        )

    def test_02_ship_pick_reschedule(self):
        """change the Ship date, then the Pick date"""
        # Set the scheduled_date of the Ship picking to next week.
        scheduled_date = datetime.now().replace(microsecond=0) + timedelta(days=7)
        propagated_date = scheduled_date + timedelta(days=7)
        self.ship.scheduled_date = scheduled_date

        # Then set the scheduled_date of the Pick picking to next week.
        self.pick.scheduled_date = scheduled_date

        delta = timedelta(seconds=2)
        # the date of the stock.move in the Pick picking is moved to next week
        self.assertAlmostEqual(
            self.pick.move_lines[0].date,
            scheduled_date,
            msg="The date of stock.move in the Pick picking should be moved to next week",
            delta=delta,
        )

        # the date of the stock.move in the Ship picking is moved to in 2 weeks
        self.assertAlmostEqual(
            self.ship.move_lines[0].date,
            propagated_date,
            msg="the date of the stock.move in the Ship picking should be moved to in 2 weeks",
            delta=delta,
        )

        # the scheduled_date of the Ship picking is moved to in 2 weeks
        self.assertAlmostEqual(
            self.ship.scheduled_date,
            propagated_date,
            msg="the scheduled_date of the Ship picking should be moved to in 2 weeks",
            delta=delta,
        )

    def test_03_ship_pick_backorder_reschedule(self):
        """backorder handling : reschedule before process chained"""
        # Set the scheduled_date of the Ship picking to next week.
        scheduled_date = datetime.now().replace(microsecond=0) + timedelta(days=7)
        propagated_date = scheduled_date + timedelta(days=7)
        self.ship.scheduled_date = scheduled_date

        # Process the picking for the available quantity of the product (2)
        self.pick.action_assign()
        self.pick.move_lines[0].quantity_done = 2.0
        self.pick._action_done()

        # Create a backorder of Pick.
        backorder_pick = self.env["stock.picking"].search(
            [("backorder_id", "=", self.pick.id)]
        )

        # Change the scheduled date of the Pick backorder to next week.
        backorder_pick.scheduled_date = scheduled_date

        delta = timedelta(seconds=2)
        # the date of the stock.move in the Ship picking is in 2 weeks
        self.assertAlmostEqual(
            self.ship.move_lines[0].date,
            propagated_date,
            msg="the date of the stock.move in the Ship picking should be moved to in 2 weeks",
            delta=delta,
        )
        # the scheduled date of the Ship picking is in 2 weeks
        self.assertAlmostEqual(
            self.ship.scheduled_date,
            propagated_date,
            msg="the scheduled_date of the Ship picking should be moved to in 2 weeks",
            delta=delta,
        )

    def test_04_ship_process_pick_multiple_backorders(self):
        """backorder handling : process chained before reschedule"""
        # Set the scheduled_date of the Ship picking to next week.
        scheduled_date = datetime.now().replace(microsecond=0) + timedelta(days=7)
        propagated_date = scheduled_date + timedelta(days=7)
        self.ship.scheduled_date = scheduled_date

        # Process the picking for the available quantity of the product (2)
        self.pick.action_assign()
        self.pick.move_lines[0].quantity_done = 2.0
        self.pick._action_done()

        # Create a backorder of Pick.
        backorder_pick = self.env["stock.picking"].search(
            [("backorder_id", "=", self.pick.id)]
        )

        # Process the Ship picking for the available quantity of the product (2)
        self.ship.action_assign()
        self.ship.move_lines[0].quantity_done = 2.0
        self.ship._action_done()

        # create a backorder of Ship
        backorder_ship = self.env["stock.picking"].search(
            [("backorder_id", "=", self.ship.id)]
        )

        # Change the scheduled date of the Pick backorder to next week.
        backorder_pick.scheduled_date = scheduled_date

        delta = timedelta(seconds=2)
        # the date of the stock.move in the Ship backorder picking is in 2 weeks
        self.assertAlmostEqual(
            backorder_ship.move_lines[0].date,
            propagated_date,
            msg="the date of the stock.move in the Ship backorder "
            "picking should be moved to in 2 weeks",
            delta=delta,
        )

        # the scheduled date of the Ship backorder picking is in 2 weeks
        self.assertAlmostEqual(
            backorder_ship.move_lines[0].date,
            propagated_date,
            msg="the scheduled_date of the Ship picking backorder "
            "should be moved to in 2 weeks",
            delta=delta,
        )
