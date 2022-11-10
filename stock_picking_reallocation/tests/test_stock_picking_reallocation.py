from datetime import datetime, timedelta

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestStockPickingReallocation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockPickingReallocation, cls).setUpClass()

        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.product_count = 5
        cls.products = []

        for i in range(1, cls.product_count + 1):
            product_i = cls.env["product.product"].create(
                {
                    "name": "Test product %d" % i,
                    "type": "product",
                }
            )
            setattr(cls, "product_%d" % i, product_i)

            inventory = cls.env["stock.inventory"].create(
                {
                    "name": "Test Inventory %d" % i,
                    "product_ids": [(6, 0, product_i.ids)],
                    "state": "confirm",
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_qty": 1000,
                                "location_id": cls.stock_location.id,
                                "product_id": product_i.id,
                                "product_uom_id": product_i.uom_id.id,
                            },
                        )
                    ],
                }
            )
            inventory.action_validate()
            cls.products.append(product_i)

        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
            }
        )
        cls.moves = []
        for i, product_i in enumerate(cls.products):
            move_i = cls.env["stock.move"].create(
                {
                    "name": "/",
                    "picking_id": cls.picking.id,
                    "picking_type_id": cls.picking.picking_type_id.id,
                    "product_id": product_i.id,
                    "product_uom_qty": 100 * (i + 1),
                    "product_uom": product_i.uom_id.id,
                    "location_id": cls.stock_location.id,
                    "location_dest_id": cls.customer_location.id,
                    "date": "2020-01-01 00:00:00",
                }
            )
            setattr(cls, "move_%d" % (i + 1), move_i)
            cls.moves.append(move_i)

    def test_stock_picking_reallocation_simple_split(self):
        self.assertEqual(self.picking.state, "draft")

        self.assertAlmostEqual(self.picking.move_lines[0].product_qty, 100)
        self.assertAlmostEqual(self.picking.move_lines[1].product_qty, 200)
        self.assertAlmostEqual(self.picking.move_lines[2].product_qty, 300)
        self.assertAlmostEqual(self.picking.move_lines[3].product_qty, 400)
        self.assertAlmostEqual(self.picking.move_lines[4].product_qty, 500)

        reallocation = (
            self.env["stock.picking.reallocation"]
            .with_context(default_picking_id=self.picking.id)
            .create(
                {
                    "picking_id": self.picking.id,
                    "state": "draft",
                    "date_2": self.picking.scheduled_date + timedelta(days=45),
                    "allocation_ids": [
                        (
                            0,
                            0,
                            {
                                "move_id": move_i.id,
                                "quantity_1": (100 * (i + 1)) / 4,
                                "quantity_2": (100 * (i + 1)) * 3 / 4,
                            },
                        )
                        for i, move_i in enumerate(self.picking.move_lines)
                    ],
                }
            )
        )

        # Can't reallocate a draft picking
        with self.assertRaises(UserError):
            reallocation.reallocate()

        self.picking.move_lines._action_confirm()
        self.picking.move_lines._action_assign()
        self.picking.action_assign()

        picking_count = self.env["stock.picking"].search_count([])
        reallocation.reallocate()

        self.assertEqual(self.picking.state, "assigned")
        self.assertEqual(reallocation.state, "done")
        self.assertEqual(self.env["stock.picking"].search_count([]), picking_count + 1)

        self.assertEqual(len(self.picking.move_lines), 5)
        self.assertAlmostEqual(self.picking.move_lines[0].product_qty, 25)
        self.assertAlmostEqual(self.picking.move_lines[0].move_line_ids.product_qty, 25)
        self.assertAlmostEqual(self.picking.move_lines[1].product_qty, 50)
        self.assertAlmostEqual(self.picking.move_lines[1].move_line_ids.product_qty, 50)
        self.assertAlmostEqual(self.picking.move_lines[2].product_qty, 75)
        self.assertAlmostEqual(self.picking.move_lines[2].move_line_ids.product_qty, 75)
        self.assertAlmostEqual(self.picking.move_lines[3].product_qty, 100)
        self.assertAlmostEqual(
            self.picking.move_lines[3].move_line_ids.product_qty, 100
        )
        self.assertAlmostEqual(self.picking.move_lines[4].product_qty, 125)
        self.assertAlmostEqual(
            self.picking.move_lines[4].move_line_ids.product_qty, 125
        )

        self.assertAlmostEqual(self.picking.move_lines[0].product_id, self.product_1)
        self.assertAlmostEqual(
            self.picking.move_lines[0].move_line_ids.product_id, self.product_1
        )
        self.assertAlmostEqual(self.picking.move_lines[1].product_id, self.product_2)
        self.assertAlmostEqual(
            self.picking.move_lines[1].move_line_ids.product_id, self.product_2
        )
        self.assertAlmostEqual(self.picking.move_lines[2].product_id, self.product_3)
        self.assertAlmostEqual(
            self.picking.move_lines[2].move_line_ids.product_id, self.product_3
        )
        self.assertAlmostEqual(self.picking.move_lines[3].product_id, self.product_4)
        self.assertAlmostEqual(
            self.picking.move_lines[3].move_line_ids.product_id, self.product_4
        )
        self.assertAlmostEqual(self.picking.move_lines[4].product_id, self.product_5)
        self.assertAlmostEqual(
            self.picking.move_lines[4].move_line_ids.product_id, self.product_5
        )

        new_picking = self.env["stock.picking"].search(
            [("backorder_id", "=", self.picking.id)]
        )
        new_picking.ensure_one()
        self.assertEqual(new_picking.state, "assigned")
        self.assertEqual(
            new_picking.scheduled_date,
            self.picking.scheduled_date + timedelta(days=45),
        )

        self.assertEqual(len(new_picking.move_lines), 5)
        self.assertAlmostEqual(new_picking.move_lines[0].product_qty, 75)
        self.assertAlmostEqual(new_picking.move_lines[0].move_line_ids.product_qty, 75)
        self.assertAlmostEqual(new_picking.move_lines[1].product_qty, 150)
        self.assertAlmostEqual(new_picking.move_lines[1].move_line_ids.product_qty, 150)
        self.assertAlmostEqual(new_picking.move_lines[2].product_qty, 225)
        self.assertAlmostEqual(new_picking.move_lines[2].move_line_ids.product_qty, 225)
        self.assertAlmostEqual(new_picking.move_lines[3].product_qty, 300)
        self.assertAlmostEqual(new_picking.move_lines[3].move_line_ids.product_qty, 300)
        self.assertAlmostEqual(new_picking.move_lines[4].product_qty, 375)
        self.assertAlmostEqual(new_picking.move_lines[4].move_line_ids.product_qty, 375)

        self.assertAlmostEqual(new_picking.move_lines[0].product_id, self.product_1)
        self.assertAlmostEqual(
            new_picking.move_lines[0].move_line_ids.product_id, self.product_1
        )
        self.assertAlmostEqual(new_picking.move_lines[1].product_id, self.product_2)
        self.assertAlmostEqual(
            new_picking.move_lines[1].move_line_ids.product_id, self.product_2
        )
        self.assertAlmostEqual(new_picking.move_lines[2].product_id, self.product_3)
        self.assertAlmostEqual(
            new_picking.move_lines[2].move_line_ids.product_id, self.product_3
        )
        self.assertAlmostEqual(new_picking.move_lines[3].product_id, self.product_4)
        self.assertAlmostEqual(
            new_picking.move_lines[3].move_line_ids.product_id, self.product_4
        )
        self.assertAlmostEqual(new_picking.move_lines[4].product_id, self.product_5)
        self.assertAlmostEqual(
            new_picking.move_lines[4].move_line_ids.product_id, self.product_5
        )

    def _reallocate(self, delays, quantities, picking=None):
        picking = picking or self.picking
        picking.move_lines._action_confirm()
        picking.move_lines._action_assign()
        picking.action_assign()

        values = {
            "picking_id": picking.id,
            "state": "draft",
            "allocation_ids": [
                (
                    0,
                    0,
                    {
                        "move_id": move_i.id,
                        **{
                            "quantity_%d" % (j + 1): value[i]
                            for j, value in enumerate(quantities)
                        },
                    },
                )
                for i, move_i in enumerate(picking.move_lines)
            ],
        }
        if len(delays) == len(quantities):
            values["date_1"] = picking.scheduled_date + timedelta(days=delays[0])
            delays = delays[1:]

        for i, delay in enumerate(delays):
            values["date_%d" % (i + 2)] = picking.scheduled_date + timedelta(days=delay)

        reallocation = (
            self.env["stock.picking.reallocation"]
            .with_context(default_picking_id=picking.id)
            .create(values)
        )
        reallocation.reallocate()

        self.assertEqual(reallocation.state, "done")

        return self.env["stock.picking"].search(
            [("backorder_id", "=", picking.id)], order="scheduled_date asc"
        )

    def test_stock_picking_reallocation_meta__reallocate(self):
        new_picking = self._reallocate(
            [45], [[25, 50, 75, 100, 125], [75, 150, 225, 300, 375]]
        )

        self.assertEqual(self.picking.state, "assigned")
        self.assertEqual(len(self.picking.move_lines), 5)
        self.assertAlmostEqual(self.picking.move_lines[0].product_qty, 25)
        self.assertAlmostEqual(self.picking.move_lines[0].move_line_ids.product_qty, 25)
        self.assertAlmostEqual(self.picking.move_lines[1].product_qty, 50)
        self.assertAlmostEqual(self.picking.move_lines[1].move_line_ids.product_qty, 50)
        self.assertAlmostEqual(self.picking.move_lines[2].product_qty, 75)
        self.assertAlmostEqual(self.picking.move_lines[2].move_line_ids.product_qty, 75)
        self.assertAlmostEqual(self.picking.move_lines[3].product_qty, 100)
        self.assertAlmostEqual(
            self.picking.move_lines[3].move_line_ids.product_qty, 100
        )
        self.assertAlmostEqual(self.picking.move_lines[4].product_qty, 125)
        self.assertAlmostEqual(
            self.picking.move_lines[4].move_line_ids.product_qty, 125
        )

        self.assertEqual(new_picking.state, "assigned")
        self.assertEqual(
            new_picking.scheduled_date,
            self.picking.scheduled_date + timedelta(days=45),
        )
        self.assertEqual(len(new_picking.move_lines), 5)
        self.assertAlmostEqual(new_picking.move_lines[0].product_qty, 75)
        self.assertAlmostEqual(new_picking.move_lines[0].move_line_ids.product_qty, 75)
        self.assertAlmostEqual(new_picking.move_lines[1].product_qty, 150)
        self.assertAlmostEqual(new_picking.move_lines[1].move_line_ids.product_qty, 150)
        self.assertAlmostEqual(new_picking.move_lines[2].product_qty, 225)
        self.assertAlmostEqual(new_picking.move_lines[2].move_line_ids.product_qty, 225)
        self.assertAlmostEqual(new_picking.move_lines[3].product_qty, 300)
        self.assertAlmostEqual(new_picking.move_lines[3].move_line_ids.product_qty, 300)
        self.assertAlmostEqual(new_picking.move_lines[4].product_qty, 375)
        self.assertAlmostEqual(new_picking.move_lines[4].move_line_ids.product_qty, 375)

    def test_stock_picking_reallocation_full(self):
        new_picking = self._reallocate(
            [45, 90, 120, 200],
            [
                [0, 50, 300, 100, 0],
                [0, 100, 0, 300, 200],
                [100, 25, 0, 0, 200],
                [0, 20, 0, 0, 100],
                [0, 5, 0, 0, 0],
            ],
        )

        self.assertEqual(len(self.picking.move_lines), 3)
        self.assertAlmostEqual(
            self.picking.move_lines.filtered(
                lambda ml: ml.product_id == self.product_2
            ).product_qty,
            50,
        )
        self.assertAlmostEqual(
            self.picking.move_lines.filtered(
                lambda ml: ml.product_id == self.product_2
            ).move_line_ids.product_qty,
            50,
        )
        self.assertAlmostEqual(
            self.picking.move_lines.filtered(
                lambda ml: ml.product_id == self.product_3
            ).product_qty,
            300,
        )
        self.assertAlmostEqual(
            self.picking.move_lines.filtered(
                lambda ml: ml.product_id == self.product_3
            ).move_line_ids.product_qty,
            300,
        )
        self.assertAlmostEqual(
            self.picking.move_lines.filtered(
                lambda ml: ml.product_id == self.product_4
            ).product_qty,
            100,
        )
        self.assertAlmostEqual(
            self.picking.move_lines.filtered(
                lambda ml: ml.product_id == self.product_4
            ).move_line_ids.product_qty,
            100,
        )

        self.assertEqual(new_picking[0].state, "assigned")
        self.assertEqual(len(new_picking[0].move_lines), 3)
        self.assertEqual(
            new_picking[0].scheduled_date,
            self.picking.scheduled_date + timedelta(days=45),
        )
        self.assertAlmostEqual(
            new_picking[0]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_2)
            .product_qty,
            100,
        )
        self.assertAlmostEqual(
            new_picking[0]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_2)
            .move_line_ids.product_qty,
            100,
        )
        self.assertAlmostEqual(
            new_picking[0]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_4)
            .product_qty,
            300,
        )
        self.assertAlmostEqual(
            new_picking[0]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_4)
            .move_line_ids.product_qty,
            300,
        )
        self.assertAlmostEqual(
            new_picking[0]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_5)
            .product_qty,
            200,
        )
        self.assertAlmostEqual(
            new_picking[0]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_5)
            .move_line_ids.product_qty,
            200,
        )

        self.assertEqual(new_picking[1].state, "assigned")
        self.assertEqual(len(new_picking[1].move_lines), 3)
        self.assertEqual(
            new_picking[1].scheduled_date,
            self.picking.scheduled_date + timedelta(days=90),
        )
        self.assertAlmostEqual(
            new_picking[1]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_1)
            .product_qty,
            100,
        )
        self.assertAlmostEqual(
            new_picking[1]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_1)
            .move_line_ids.product_qty,
            100,
        )
        self.assertAlmostEqual(
            new_picking[1]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_2)
            .product_qty,
            25,
        )
        self.assertAlmostEqual(
            new_picking[1]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_2)
            .move_line_ids.product_qty,
            25,
        )
        self.assertAlmostEqual(
            new_picking[1]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_5)
            .product_qty,
            200,
        )
        self.assertAlmostEqual(
            new_picking[1]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_5)
            .move_line_ids.product_qty,
            200,
        )

        self.assertEqual(new_picking[2].state, "assigned")
        self.assertEqual(len(new_picking[2].move_lines), 2)
        self.assertEqual(
            new_picking[2].scheduled_date,
            self.picking.scheduled_date + timedelta(days=120),
        )
        self.assertAlmostEqual(
            new_picking[2]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_2)
            .product_qty,
            20,
        )
        self.assertAlmostEqual(
            new_picking[2]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_2)
            .move_line_ids.product_qty,
            20,
        )
        self.assertAlmostEqual(
            new_picking[2]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_5)
            .product_qty,
            100,
        )
        self.assertAlmostEqual(
            new_picking[2]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_5)
            .move_line_ids.product_qty,
            100,
        )

        self.assertEqual(new_picking[3].state, "assigned")
        self.assertEqual(len(new_picking[3].move_lines), 1)
        self.assertEqual(
            new_picking[3].scheduled_date,
            self.picking.scheduled_date + timedelta(days=200),
        )
        self.assertAlmostEqual(
            new_picking[3]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_2)
            .product_qty,
            5,
        )
        self.assertAlmostEqual(
            new_picking[3]
            .move_lines.filtered(lambda ml: ml.product_id == self.product_2)
            .move_line_ids.product_qty,
            5,
        )

    def test_stock_picking_reallocation_underflow_repartition(self):
        with self.assertRaises(UserError) as e:
            self._reallocate(
                [45, 90],
                [
                    [100, 0, 0, 300, 500],
                    [0, 200, 0, 99, 0],
                    [0, 0, 300, 0, 0],
                ],
            )
        self.assertEqual(
            e.exception.args[0],
            "There is still 1.00 to allocate for Test product 4.",
        )

    def test_stock_picking_reallocation_overflow_repartition(self):
        with self.assertRaises(UserError) as e:
            self._reallocate(
                [45, 90],
                [
                    [100, 0, 0, 300, 490],
                    [0, 200, 0, 100, 11],
                    [0, 0, 300, 0, 0],
                ],
            )
        self.assertEqual(
            e.exception.args[0],
            "There is an excess of 1.00 in allocation of Test product 5.",
        )

    def test_stock_picking_reallocation_overflow_with_previous_fit_repartition(self):
        with self.assertRaises(UserError) as e:
            self._reallocate(
                [45, 90],
                [
                    [100, 0, 0, 300, 490],
                    [0, 200, 0, 100, 10],
                    [0, 0, 300, 0, 1],
                ],
            )
        self.assertEqual(
            e.exception.args[0],
            "There is an excess of 1.00 in allocation of Test product 5.",
        )

    def test_stock_picking_reallocation_work_for_done_qty_lower_than_final_demand(self):
        self.move_1.quantity_done = 80
        self._reallocate(
            [45, 90],
            [
                [100, 0, 0, 300, 490],
                [0, 200, 0, 100, 10],
                [0, 0, 300, 0, 0],
            ],
        )
        self.assertEqual(self.move_1.quantity_done, 80)

    def test_stock_picking_reallocation_work_for_done_qty_higher_than_final_demand(
        self,
    ):
        self.move_1.quantity_done = 80

        with self.assertRaises(UserError) as e:
            self._reallocate(
                [45, 90],
                [
                    [50, 0, 0, 300, 490],
                    [50, 200, 0, 100, 10],
                    [0, 0, 300, 0, 0],
                ],
            )
        self.assertEqual(
            e.exception.args[0],
            "Cannot allocate less in current picking (50.00) than what was "
            "already done for Test product 1 (80.00)",
        )

    def test_stock_picking_reallocation_rereallocation(self):
        new_picking_1, new_picking_2 = self._reallocate(
            [45, 90],
            [
                [50, 0, 0, 300, 490],
                [50, 150, 0, 100, 10],
                [0, 50, 300, 0, 0],
            ],
        )
        new_picking_1_1 = self._reallocate(
            [120],
            [
                [20, 0, 75, 10],
                [30, 150, 25, 0],
            ],
            new_picking_1,
        )
        new_picking_2_1 = self._reallocate(
            [160],
            [
                [50, 200],
                [0, 100],
            ],
            new_picking_2,
        )

        self.assertEqual(new_picking_1.state, "assigned")
        self.assertEqual(len(new_picking_1.move_lines), 3)
        self.assertEqual(
            new_picking_1.scheduled_date,
            self.picking.scheduled_date + timedelta(days=45),
        )
        self.assertAlmostEqual(
            new_picking_1.move_lines.filtered(
                lambda ml: ml.product_id == self.product_1
            ).product_qty,
            20,
        )
        self.assertAlmostEqual(
            new_picking_1.move_lines.filtered(
                lambda ml: ml.product_id == self.product_1
            ).move_line_ids.product_qty,
            20,
        )
        self.assertAlmostEqual(
            new_picking_1.move_lines.filtered(
                lambda ml: ml.product_id == self.product_4
            ).product_qty,
            75,
        )
        self.assertAlmostEqual(
            new_picking_1.move_lines.filtered(
                lambda ml: ml.product_id == self.product_4
            ).move_line_ids.product_qty,
            75,
        )
        self.assertAlmostEqual(
            new_picking_1.move_lines.filtered(
                lambda ml: ml.product_id == self.product_5
            ).product_qty,
            10,
        )
        self.assertAlmostEqual(
            new_picking_1.move_lines.filtered(
                lambda ml: ml.product_id == self.product_5
            ).move_line_ids.product_qty,
            10,
        )

        self.assertEqual(new_picking_1_1.state, "assigned")
        self.assertEqual(len(new_picking_1_1.move_lines), 3)
        self.assertEqual(
            new_picking_1_1.scheduled_date,
            self.picking.scheduled_date + timedelta(days=45 + 120),
        )
        self.assertAlmostEqual(
            new_picking_1_1.move_lines.filtered(
                lambda ml: ml.product_id == self.product_1
            ).product_qty,
            30,
        )
        self.assertAlmostEqual(
            new_picking_1_1.move_lines.filtered(
                lambda ml: ml.product_id == self.product_1
            ).move_line_ids.product_qty,
            30,
        )
        self.assertAlmostEqual(
            new_picking_1_1.move_lines.filtered(
                lambda ml: ml.product_id == self.product_2
            ).product_qty,
            150,
        )
        self.assertAlmostEqual(
            new_picking_1_1.move_lines.filtered(
                lambda ml: ml.product_id == self.product_2
            ).move_line_ids.product_qty,
            150,
        )
        self.assertAlmostEqual(
            new_picking_1_1.move_lines.filtered(
                lambda ml: ml.product_id == self.product_4
            ).product_qty,
            25,
        )
        self.assertAlmostEqual(
            new_picking_1_1.move_lines.filtered(
                lambda ml: ml.product_id == self.product_4
            ).move_line_ids.product_qty,
            25,
        )

        self.assertEqual(new_picking_2.state, "assigned")
        self.assertEqual(len(new_picking_2.move_lines), 2)
        self.assertEqual(
            new_picking_2.scheduled_date,
            self.picking.scheduled_date + timedelta(days=90),
        )
        self.assertAlmostEqual(
            new_picking_2.move_lines.filtered(
                lambda ml: ml.product_id == self.product_2
            ).product_qty,
            50,
        )
        self.assertAlmostEqual(
            new_picking_2.move_lines.filtered(
                lambda ml: ml.product_id == self.product_2
            ).move_line_ids.product_qty,
            50,
        )
        self.assertAlmostEqual(
            new_picking_2.move_lines.filtered(
                lambda ml: ml.product_id == self.product_3
            ).product_qty,
            200,
        )
        self.assertAlmostEqual(
            new_picking_2.move_lines.filtered(
                lambda ml: ml.product_id == self.product_3
            ).move_line_ids.product_qty,
            200,
        )
        self.assertEqual(new_picking_2_1.state, "assigned")
        self.assertEqual(len(new_picking_2_1.move_lines), 1)
        self.assertEqual(
            new_picking_2_1.scheduled_date,
            self.picking.scheduled_date + timedelta(days=90 + 160),
        )
        self.assertAlmostEqual(
            new_picking_2_1.move_lines.filtered(
                lambda ml: ml.product_id == self.product_3
            ).product_qty,
            100,
        )
        self.assertAlmostEqual(
            new_picking_2_1.move_lines.filtered(
                lambda ml: ml.product_id == self.product_3
            ).move_line_ids.product_qty,
            100,
        )

    def test_stock_picking_cancel(self):
        reallocation = (
            self.env["stock.picking.reallocation"]
            .with_context(default_picking_id=self.picking.id)
            .create(
                {
                    "picking_id": self.picking.id,
                    "state": "draft",
                    "date_2": self.picking.scheduled_date + timedelta(days=45),
                    "allocation_ids": [
                        (
                            0,
                            0,
                            {
                                "move_id": move_i.id,
                                "quantity_1": (100 * (i + 1)) / 4,
                                "quantity_2": (100 * (i + 1)) * 3 / 4,
                            },
                        )
                        for i, move_i in enumerate(self.picking.move_lines)
                    ],
                }
            )
        )
        reallocation.cancel()
        self.assertEqual(reallocation.state, "cancel")

    def _get_allocation(self, *values):
        reallocation = (
            self.env["stock.picking.reallocation"]
            .with_context(default_picking_id=self.picking.id)
            .create(
                {
                    "state": "draft",
                    "date_2": self.picking.scheduled_date + timedelta(days=45),
                    "date_3": self.picking.scheduled_date + timedelta(days=90),
                    "date_4": self.picking.scheduled_date + timedelta(days=120),
                    "date_5": self.picking.scheduled_date + timedelta(days=150),
                    "allocation_ids": [
                        (
                            0,
                            0,
                            {
                                "move_id": self.move_1.id,
                                **{
                                    "quantity_%d" % (i + 1): value
                                    for i, value in enumerate(values)
                                },
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "move_id": self.move_2.id,
                                "quantity_1": 196,
                                "quantity_2": 1,
                                "quantity_3": 1,
                                "quantity_4": 1,
                                "quantity_5": 1,
                            },
                        ),
                    ],
                }
            )
        )
        return reallocation.allocation_ids.filtered(
            lambda allocation: allocation.move_id == self.move_1
        ).ensure_one()

    def test_stock_picking_allocation_repartition_overflow_focus_lower(self):
        allocation = self._get_allocation(100, 10, 0, 0, 0)

        allocation._update_quantities(2)

        self.assertEqual(allocation.quantity_1, 90)
        self.assertEqual(allocation.quantity_2, 10)
        self.assertEqual(allocation.quantity_3, 0)
        self.assertEqual(allocation.quantity_4, 0)
        self.assertEqual(allocation.quantity_5, 0)

    def test_stock_picking_allocation_repartition_overflow_focus_higher(self):
        allocation = self._get_allocation(100, 10, 0, 0, 0)

        allocation._update_quantities(1)

        self.assertEqual(allocation.quantity_1, 100)
        self.assertEqual(allocation.quantity_2, 0)
        self.assertEqual(allocation.quantity_3, 0)
        self.assertEqual(allocation.quantity_4, 0)
        self.assertEqual(allocation.quantity_5, 0)

    def test_stock_picking_allocation_repartition_overflow_focus_another(self):
        allocation = self._get_allocation(100, 10, 0, 0, 0)

        allocation._update_quantities(5)

        self.assertEqual(allocation.quantity_1, 90)
        self.assertEqual(allocation.quantity_2, 10)
        self.assertEqual(allocation.quantity_3, 0)
        self.assertEqual(allocation.quantity_4, 0)
        self.assertEqual(allocation.quantity_5, 0)

    def test_stock_picking_allocation_repartition_underflow_focus_lower(self):
        allocation = self._get_allocation(80, 10, 0, 0, 0)

        allocation._update_quantities(2)

        self.assertEqual(allocation.quantity_1, 90)
        self.assertEqual(allocation.quantity_2, 10)
        self.assertEqual(allocation.quantity_3, 0)
        self.assertEqual(allocation.quantity_4, 0)
        self.assertEqual(allocation.quantity_5, 0)

    def test_stock_picking_allocation_repartition_underflow_focus_higher(self):
        allocation = self._get_allocation(80, 10, 0, 0, 0)

        allocation._update_quantities(1)

        self.assertEqual(allocation.quantity_1, 80)
        self.assertEqual(allocation.quantity_2, 20)
        self.assertEqual(allocation.quantity_3, 0)
        self.assertEqual(allocation.quantity_4, 0)
        self.assertEqual(allocation.quantity_5, 0)

    def test_stock_picking_allocation_repartition_underflow_focus_another(self):
        allocation = self._get_allocation(80, 10, 0, 0, 0)

        allocation._update_quantities(5)

        self.assertEqual(allocation.quantity_1, 90)
        self.assertEqual(allocation.quantity_2, 10)
        self.assertEqual(allocation.quantity_3, 0)
        self.assertEqual(allocation.quantity_4, 0)
        self.assertEqual(allocation.quantity_5, 0)

    def test_stock_picking_reallocation_on_multiple_move_move_lines(
        self,
    ):
        # Create the stock.move.line
        self.picking.action_assign()

        self.move_1.move_line_ids.ensure_one().product_uom_qty = 70

        # Add a second move.line
        self.env["stock.move.line"].create(
            {
                "move_id": self.move_1.id,
                "product_id": self.product_1.id,
                "product_uom_id": self.move_1.product_uom.id,
                "location_id": self.move_1.location_id.id,
                "location_dest_id": self.move_1.location_dest_id.id,
                "picking_id": self.picking.id,
                "company_id": self.move_1.company_id.id,
                "product_uom_qty": 30,
            }
        )
        self.assertEqual(len(self.move_1.move_line_ids), 2)

        with self.assertRaises(UserError) as e:
            self._reallocate(
                [45, 90],
                [
                    [50, 0, 0, 300, 490],
                    [50, 200, 0, 100, 10],
                    [0, 0, 300, 0, 0],
                ],
            )
        self.assertEqual(
            e.exception.args[0],
            "Cannot reallocate a move with multiple move lines for product "
            "Test product 1",
        )

    def test_stock_picking_reallocation_dates_ordered(self):
        new_picking = self._reallocate(
            [10, 20],
            [
                [97, 194, 291, 388, 485],
                [1, 2, 3, 4, 5],
                [2, 4, 6, 8, 10],
            ],
        )

        ml_date = datetime(2020, 1, 1)
        self.assertEqual(self.picking.scheduled_date, ml_date)
        ml = self.picking.move_lines
        self.assertAlmostEqual(ml[0].product_qty, 97)
        self.assertAlmostEqual(ml[0].move_line_ids.product_qty, 97)
        self.assertEqual(ml[0].date, ml_date)
        self.assertAlmostEqual(ml[1].product_qty, 194)
        self.assertAlmostEqual(ml[1].move_line_ids.product_qty, 194)
        self.assertEqual(ml[1].date, ml_date)
        self.assertAlmostEqual(ml[2].product_qty, 291)
        self.assertAlmostEqual(ml[2].move_line_ids.product_qty, 291)
        self.assertEqual(ml[2].date, ml_date)
        self.assertAlmostEqual(ml[3].product_qty, 388)
        self.assertAlmostEqual(ml[3].move_line_ids.product_qty, 388)
        self.assertEqual(ml[3].date, ml_date)
        self.assertAlmostEqual(ml[4].product_qty, 485)
        self.assertAlmostEqual(ml[4].move_line_ids.product_qty, 485)
        self.assertEqual(ml[4].date, ml_date)

        ml_date = datetime(2020, 1, 11)
        self.assertEqual(new_picking[0].scheduled_date, ml_date)
        ml = new_picking[0].move_lines
        self.assertAlmostEqual(ml[0].product_qty, 1)
        self.assertAlmostEqual(ml[0].move_line_ids.product_qty, 1)
        self.assertEqual(ml[0].date, ml_date)
        self.assertAlmostEqual(ml[1].product_qty, 2)
        self.assertAlmostEqual(ml[1].move_line_ids.product_qty, 2)
        self.assertEqual(ml[1].date, ml_date)
        self.assertAlmostEqual(ml[2].product_qty, 3)
        self.assertAlmostEqual(ml[2].move_line_ids.product_qty, 3)
        self.assertEqual(ml[2].date, ml_date)
        self.assertAlmostEqual(ml[3].product_qty, 4)
        self.assertAlmostEqual(ml[3].move_line_ids.product_qty, 4)
        self.assertEqual(ml[3].date, ml_date)
        self.assertAlmostEqual(ml[4].product_qty, 5)
        self.assertAlmostEqual(ml[4].move_line_ids.product_qty, 5)
        self.assertEqual(ml[4].date, ml_date)

        ml_date = datetime(2020, 1, 21)
        self.assertEqual(new_picking[1].scheduled_date, ml_date)
        ml = new_picking[1].move_lines
        self.assertAlmostEqual(ml[0].product_qty, 2)
        self.assertAlmostEqual(ml[0].move_line_ids.product_qty, 2)
        self.assertEqual(ml[0].date, ml_date)
        self.assertAlmostEqual(ml[1].product_qty, 4)
        self.assertAlmostEqual(ml[1].move_line_ids.product_qty, 4)
        self.assertEqual(ml[1].date, ml_date)
        self.assertAlmostEqual(ml[2].product_qty, 6)
        self.assertAlmostEqual(ml[2].move_line_ids.product_qty, 6)
        self.assertEqual(ml[2].date, ml_date)
        self.assertAlmostEqual(ml[3].product_qty, 8)
        self.assertAlmostEqual(ml[3].move_line_ids.product_qty, 8)
        self.assertEqual(ml[3].date, ml_date)
        self.assertAlmostEqual(ml[4].product_qty, 10)
        self.assertAlmostEqual(ml[4].move_line_ids.product_qty, 10)
        self.assertEqual(ml[4].date, ml_date)

    def test_stock_picking_reallocation_dates_unordered_1(self):
        new_picking = self._reallocate(
            [-20, 10],
            [
                [97, 194, 291, 388, 485],
                [1, 2, 3, 4, 5],
                [2, 4, 6, 8, 10],
            ],
        )

        ml_date = datetime(2019, 12, 12)
        self.assertEqual(self.picking.scheduled_date, ml_date)
        ml = self.picking.move_lines
        self.assertAlmostEqual(ml[0].product_qty, 1)
        self.assertAlmostEqual(ml[0].move_line_ids.product_qty, 1)
        self.assertEqual(ml[0].date, ml_date)
        self.assertAlmostEqual(ml[1].product_qty, 2)
        self.assertAlmostEqual(ml[1].move_line_ids.product_qty, 2)
        self.assertEqual(ml[1].date, ml_date)
        self.assertAlmostEqual(ml[2].product_qty, 3)
        self.assertAlmostEqual(ml[2].move_line_ids.product_qty, 3)
        self.assertEqual(ml[2].date, ml_date)
        self.assertAlmostEqual(ml[3].product_qty, 4)
        self.assertAlmostEqual(ml[3].move_line_ids.product_qty, 4)
        self.assertEqual(ml[3].date, ml_date)
        self.assertAlmostEqual(ml[4].product_qty, 5)
        self.assertAlmostEqual(ml[4].move_line_ids.product_qty, 5)
        self.assertEqual(ml[4].date, ml_date)

        ml_date = datetime(2020, 1, 1)
        self.assertEqual(new_picking[0].scheduled_date, ml_date)
        ml = new_picking[0].move_lines
        self.assertAlmostEqual(ml[0].product_qty, 97)
        self.assertAlmostEqual(ml[0].move_line_ids.product_qty, 97)
        self.assertEqual(ml[0].date, ml_date)
        self.assertAlmostEqual(ml[1].product_qty, 194)
        self.assertAlmostEqual(ml[1].move_line_ids.product_qty, 194)
        self.assertEqual(ml[1].date, ml_date)
        self.assertAlmostEqual(ml[2].product_qty, 291)
        self.assertAlmostEqual(ml[2].move_line_ids.product_qty, 291)
        self.assertEqual(ml[2].date, ml_date)
        self.assertAlmostEqual(ml[3].product_qty, 388)
        self.assertAlmostEqual(ml[3].move_line_ids.product_qty, 388)
        self.assertEqual(ml[3].date, ml_date)
        self.assertAlmostEqual(ml[4].product_qty, 485)
        self.assertAlmostEqual(ml[4].move_line_ids.product_qty, 485)
        self.assertEqual(ml[4].date, ml_date)

        ml_date = datetime(2020, 1, 11)
        self.assertEqual(new_picking[1].scheduled_date, ml_date)
        ml = new_picking[1].move_lines
        self.assertAlmostEqual(ml[0].product_qty, 2)
        self.assertAlmostEqual(ml[0].move_line_ids.product_qty, 2)
        self.assertEqual(ml[0].date, ml_date)
        self.assertAlmostEqual(ml[1].product_qty, 4)
        self.assertAlmostEqual(ml[1].move_line_ids.product_qty, 4)
        self.assertEqual(ml[1].date, ml_date)
        self.assertAlmostEqual(ml[2].product_qty, 6)
        self.assertAlmostEqual(ml[2].move_line_ids.product_qty, 6)
        self.assertEqual(ml[2].date, ml_date)
        self.assertAlmostEqual(ml[3].product_qty, 8)
        self.assertAlmostEqual(ml[3].move_line_ids.product_qty, 8)
        self.assertEqual(ml[3].date, ml_date)
        self.assertAlmostEqual(ml[4].product_qty, 10)
        self.assertAlmostEqual(ml[4].move_line_ids.product_qty, 10)
        self.assertEqual(ml[4].date, ml_date)

    def test_stock_picking_reallocation_dates_unordered_2(self):
        new_picking = self._reallocate(
            [45, 15, 10],
            [
                [97, 194, 291, 388, 485],
                [1, 2, 3, 4, 5],
                [2, 4, 6, 8, 10],
            ],
        )

        ml_date = datetime(2020, 1, 11)
        self.assertEqual(self.picking.scheduled_date, ml_date)
        ml = self.picking.move_lines
        self.assertAlmostEqual(ml[0].product_qty, 2)
        self.assertAlmostEqual(ml[0].move_line_ids.product_qty, 2)
        self.assertEqual(ml[0].date, ml_date)
        self.assertAlmostEqual(ml[1].product_qty, 4)
        self.assertAlmostEqual(ml[1].move_line_ids.product_qty, 4)
        self.assertEqual(ml[1].date, ml_date)
        self.assertAlmostEqual(ml[2].product_qty, 6)
        self.assertAlmostEqual(ml[2].move_line_ids.product_qty, 6)
        self.assertEqual(ml[2].date, ml_date)
        self.assertAlmostEqual(ml[3].product_qty, 8)
        self.assertAlmostEqual(ml[3].move_line_ids.product_qty, 8)
        self.assertEqual(ml[3].date, ml_date)
        self.assertAlmostEqual(ml[4].product_qty, 10)
        self.assertAlmostEqual(ml[4].move_line_ids.product_qty, 10)
        self.assertEqual(ml[4].date, ml_date)

        ml_date = datetime(2020, 1, 16)
        self.assertEqual(new_picking[0].scheduled_date, ml_date)
        ml = new_picking[0].move_lines
        self.assertAlmostEqual(ml[0].product_qty, 1)
        self.assertAlmostEqual(ml[0].move_line_ids.product_qty, 1)
        self.assertEqual(ml[0].date, ml_date)
        self.assertAlmostEqual(ml[1].product_qty, 2)
        self.assertAlmostEqual(ml[1].move_line_ids.product_qty, 2)
        self.assertEqual(ml[1].date, ml_date)
        self.assertAlmostEqual(ml[2].product_qty, 3)
        self.assertAlmostEqual(ml[2].move_line_ids.product_qty, 3)
        self.assertEqual(ml[2].date, ml_date)
        self.assertAlmostEqual(ml[3].product_qty, 4)
        self.assertAlmostEqual(ml[3].move_line_ids.product_qty, 4)
        self.assertEqual(ml[3].date, ml_date)
        self.assertAlmostEqual(ml[4].product_qty, 5)
        self.assertAlmostEqual(ml[4].move_line_ids.product_qty, 5)
        self.assertEqual(ml[4].date, ml_date)

        ml_date = datetime(2020, 2, 15)
        self.assertEqual(new_picking[1].scheduled_date, ml_date)
        ml = new_picking[1].move_lines
        self.assertAlmostEqual(ml[0].product_qty, 97)
        self.assertAlmostEqual(ml[0].move_line_ids.product_qty, 97)
        self.assertEqual(ml[0].date, ml_date)
        self.assertAlmostEqual(ml[1].product_qty, 194)
        self.assertAlmostEqual(ml[1].move_line_ids.product_qty, 194)
        self.assertEqual(ml[1].date, ml_date)
        self.assertAlmostEqual(ml[2].product_qty, 291)
        self.assertAlmostEqual(ml[2].move_line_ids.product_qty, 291)
        self.assertEqual(ml[2].date, ml_date)
        self.assertAlmostEqual(ml[3].product_qty, 388)
        self.assertAlmostEqual(ml[3].move_line_ids.product_qty, 388)
        self.assertEqual(ml[3].date, ml_date)
        self.assertAlmostEqual(ml[4].product_qty, 485)
        self.assertAlmostEqual(ml[4].move_line_ids.product_qty, 485)
        self.assertEqual(ml[4].date, ml_date)

    def test_stock_picking_reallocation_dates_ordered_with_extra_move(self):
        self.env["stock.move"].create(
            {
                "name": "/",
                "picking_id": self.picking.id,
                "picking_type_id": self.picking.picking_type_id.id,
                "product_id": self.products[0].id,
                "product_uom_qty": 2,
                "product_uom": self.products[0].uom_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "date": "2020-07-23 00:00:00",
            }
        )

        new_picking = self._reallocate(
            [10, 15],
            [
                [102, 198, 297, 396, 495],
                [0, 2, 3, 4, 5],
            ],
        )

        ml_date = datetime(2020, 1, 11)
        self.assertEqual(self.picking.scheduled_date, ml_date)
        ml = self.picking.move_lines
        self.assertAlmostEqual(ml[0].product_qty, 102)
        self.assertAlmostEqual(ml[0].move_line_ids.product_qty, 102)
        self.assertEqual(ml[0].date, ml_date)
        self.assertAlmostEqual(ml[1].product_qty, 198)
        self.assertAlmostEqual(ml[1].move_line_ids.product_qty, 198)
        self.assertEqual(ml[1].date, ml_date)
        self.assertAlmostEqual(ml[2].product_qty, 297)
        self.assertAlmostEqual(ml[2].move_line_ids.product_qty, 297)
        self.assertEqual(ml[2].date, ml_date)
        self.assertAlmostEqual(ml[3].product_qty, 396)
        self.assertAlmostEqual(ml[3].move_line_ids.product_qty, 396)
        self.assertEqual(ml[3].date, ml_date)
        self.assertAlmostEqual(ml[4].product_qty, 495)
        self.assertAlmostEqual(ml[4].move_line_ids.product_qty, 495)
        self.assertEqual(ml[4].date, ml_date)

        ml_date = datetime(2020, 1, 16)
        self.assertEqual(new_picking[0].scheduled_date, ml_date)
        ml = new_picking[0].move_lines
        self.assertAlmostEqual(ml[0].product_qty, 2)
        self.assertAlmostEqual(ml[0].move_line_ids.product_qty, 2)
        self.assertEqual(ml[0].date, ml_date)
        self.assertAlmostEqual(ml[1].product_qty, 3)
        self.assertAlmostEqual(ml[1].move_line_ids.product_qty, 3)
        self.assertEqual(ml[1].date, ml_date)
        self.assertAlmostEqual(ml[2].product_qty, 4)
        self.assertAlmostEqual(ml[2].move_line_ids.product_qty, 4)
        self.assertEqual(ml[2].date, ml_date)
        self.assertAlmostEqual(ml[3].product_qty, 5)
        self.assertAlmostEqual(ml[3].move_line_ids.product_qty, 5)
        self.assertEqual(ml[3].date, ml_date)
