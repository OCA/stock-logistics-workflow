#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime

from odoo.tests import Form, TransactionCase


class TestStockPickingBatchGrouped(TransactionCase):
    @classmethod
    def _create_picking(cls, partner, picking_type, product, quantity):
        picking_form = Form(cls.env["stock.picking"])
        picking_form.partner_id = partner
        picking_form.picking_type_id = picking_type
        with picking_form.move_ids_without_package.new() as line:
            line.product_id = product
            line.product_uom_qty = quantity
        picking = picking_form.save()
        return picking

    @classmethod
    def _create_batch(cls, pickings):
        batch_wizard = (
            cls.env["stock.picking.to.batch"]
            .with_context(
                active_model=pickings._name,
                active_ids=pickings.ids,
            )
            .create({})
        )
        batch_wizard.attach_pickings()
        batch = pickings.batch_id
        return batch

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.old_datetime = datetime.datetime(2019, month=1, day=1)
        cls.new_datetime = datetime.datetime(2020, month=1, day=1)
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test grouped Batch Partner",
            }
        )

        cls.product_1, cls.product_2 = cls.env["product.product"].create(
            [
                {
                    "name": "Test grouped Batch Product 1",
                    "type": "product",
                },
                {
                    "name": "Test grouped Batch Product 2",
                    "type": "product",
                },
            ]
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_1, cls.stock_location, 150
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_2, cls.stock_location, 100
        )

        cls.picking_1 = cls._create_picking(
            cls.partner, cls.picking_type_out, cls.product_1, 50
        )
        cls.picking_2 = cls._create_picking(
            cls.partner, cls.picking_type_out, cls.product_1, 100
        )
        cls.picking_3 = cls._create_picking(
            cls.partner, cls.picking_type_out, cls.product_2, 100
        )

        cls.batch = cls._create_batch(cls.picking_1 | cls.picking_2 | cls.picking_3)
        cls.picking_1.move_line_ids.date = cls.new_datetime
        cls.picking_2.move_line_ids.date = cls.old_datetime
        cls.picking_3.move_line_ids.date = cls.new_datetime

    def test_grouped_lines(self):
        """Grouped lines have the same information of the move lines,
        but grouped."""
        # Arrange
        batch = self.batch
        # pre-condition
        move_lines_data = [
            {
                "product": ml.product_id,
                "reserved_qty": ml.reserved_qty,
                "qty_done": ml.qty_done,
            }
            for ml in batch.move_line_ids
        ]
        self.assertCountEqual(
            move_lines_data,
            [
                {
                    "product": self.product_1,
                    "reserved_qty": 100,
                    "qty_done": 0,
                },
                {
                    "product": self.product_1,
                    "reserved_qty": 50,
                    "qty_done": 0,
                },
                {
                    "product": self.product_2,
                    "reserved_qty": 100,
                    "qty_done": 0,
                },
            ],
        )

        # Assert
        grouped_lines_data = [
            {
                "product": gl.product_id,
                "reserved_qty": gl.reserved_qty,
                "done_qty": gl.done_qty,
            }
            for gl in batch.grouped_line_ids
        ]
        self.assertCountEqual(
            grouped_lines_data,
            [
                {
                    "product": self.product_1,
                    "reserved_qty": 150,
                    "done_qty": 0,
                },
                {
                    "product": self.product_2,
                    "reserved_qty": 100,
                    "done_qty": 0,
                },
            ],
        )

    def test_grouped_lines_set_done_qty(self):
        """Assigning quantity to the grouped lines
        spreads the quantity on the move lines."""
        # Arrange
        batch = self.batch
        old_datetime = self.old_datetime
        new_datetime = self.new_datetime
        # pre-condition
        grouped_lines_data = [
            {
                "product": gl.product_id,
                "reserved_qty": gl.reserved_qty,
                "done_qty": gl.done_qty,
            }
            for gl in batch.grouped_line_ids
        ]
        self.assertCountEqual(
            grouped_lines_data,
            [
                {
                    "product": self.product_1,
                    "reserved_qty": 150,
                    "done_qty": 0,
                },
                {
                    "product": self.product_2,
                    "reserved_qty": 100,
                    "done_qty": 0,
                },
            ],
        )

        # Act
        product_1_line = batch.grouped_line_ids.filtered(
            lambda p: p.product_id == self.product_1
        )
        product_1_line.done_qty = 130

        # Assert
        move_lines_data = [
            {
                "product": ml.product_id,
                "date": ml.date,
                "reserved_qty": ml.reserved_qty,
                "qty_done": ml.qty_done,
            }
            for ml in batch.move_line_ids
        ]
        self.assertCountEqual(
            move_lines_data,
            [
                {
                    "product": self.product_1,
                    "date": old_datetime,
                    "reserved_qty": 100,
                    "qty_done": 100,
                },
                {
                    "product": self.product_1,
                    "date": new_datetime,
                    "reserved_qty": 50,
                    "qty_done": 30,
                },
                {
                    "product": self.product_2,
                    "date": new_datetime,
                    "reserved_qty": 100,
                    "qty_done": 0,
                },
            ],
        )

        # Act: Assign more than reserved
        product_1_line.done_qty = 200

        # Assert: Extra amount has been assigned to last line
        move_lines_data = [
            {
                "product": ml.product_id,
                "date": ml.date,
                "reserved_qty": ml.reserved_qty,
                "qty_done": ml.qty_done,
            }
            for ml in batch.move_line_ids
        ]
        self.assertCountEqual(
            move_lines_data,
            [
                {
                    "product": self.product_1,
                    "date": old_datetime,
                    "reserved_qty": 100,
                    "qty_done": 100,
                },
                {
                    "product": self.product_1,
                    "date": new_datetime,
                    "reserved_qty": 50,
                    "qty_done": 100,
                },
                {
                    "product": self.product_2,
                    "date": new_datetime,
                    "reserved_qty": 100,
                    "qty_done": 0,
                },
            ],
        )

        # Act: Assign less than reserved
        product_1_line.done_qty = 20

        # Assert: Missing amount has been removed from lines
        move_lines_data = [
            {
                "product": ml.product_id,
                "date": ml.date,
                "reserved_qty": ml.reserved_qty,
                "qty_done": ml.qty_done,
            }
            for ml in batch.move_line_ids
        ]
        self.assertCountEqual(
            move_lines_data,
            [
                {
                    "product": self.product_1,
                    "date": old_datetime,
                    "reserved_qty": 100,
                    "qty_done": 20,
                },
                {
                    "product": self.product_1,
                    "date": new_datetime,
                    "reserved_qty": 50,
                    "qty_done": 0,
                },
                {
                    "product": self.product_2,
                    "date": new_datetime,
                    "reserved_qty": 100,
                    "qty_done": 0,
                },
            ],
        )

    def test_grouped_lines_set_UI_done_qty(self):
        """Done Quantity can be assigned from the UI."""
        # Arrange
        batch = self.batch
        # pre-condition
        grouped_lines_data = [
            {
                "product": gl.product_id,
                "reserved_qty": gl.reserved_qty,
                "done_qty": gl.done_qty,
            }
            for gl in batch.grouped_line_ids
        ]
        self.assertCountEqual(
            grouped_lines_data,
            [
                {
                    "product": self.product_1,
                    "reserved_qty": 150,
                    "done_qty": 0,
                },
                {
                    "product": self.product_2,
                    "reserved_qty": 100,
                    "done_qty": 0,
                },
            ],
        )

        # Act
        with Form(batch) as batch_form:
            grouped_lines_form = batch_form.grouped_line_ids
            for line_index in range(len(grouped_lines_form)):
                with grouped_lines_form.edit(line_index) as line:
                    line.done_qty = 10

        # Assert
        grouped_lines_data = [
            {
                "product": gl.product_id,
                "reserved_qty": gl.reserved_qty,
                "done_qty": gl.done_qty,
            }
            for gl in batch.grouped_line_ids
        ]
        self.assertCountEqual(
            grouped_lines_data,
            [
                {
                    "product": self.product_1,
                    "reserved_qty": 150,
                    "done_qty": 10,
                },
                {
                    "product": self.product_2,
                    "reserved_qty": 100,
                    "done_qty": 10,
                },
            ],
        )
