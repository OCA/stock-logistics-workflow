# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class CommonStockLotTraceabilityCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product1, cls.product2, cls.product3 = cls.env["product.product"].create(
            [
                {"name": "Product 1", "type": "product", "tracking": "lot"},
                {"name": "Product 2", "type": "product", "tracking": "lot"},
                {"name": "Product 3", "type": "product", "tracking": "lot"},
            ]
        )
        # Simulate a manufacture operation without any BoM nor mrp-like dependency
        # In our example:
        # - Product 1 is simply on stock
        # - Product 2 is produced from Product 1
        # - Product 3 is produced from Product 2
        # - We have/produce two lots for each product
        cls.product1_lot1, cls.product1_lot2 = cls.env["stock.production.lot"].create(
            [
                {
                    "name": "Product 1 Lot 1",
                    "product_id": cls.product1.id,
                    "company_id": cls.env.company.id,
                },
                {
                    "name": "Product 1 Lot 2",
                    "product_id": cls.product1.id,
                    "company_id": cls.env.company.id,
                },
            ]
        )
        cls.product2_lot1, cls.product2_lot2 = cls.env["stock.production.lot"].create(
            [
                {
                    "name": "Product 2 Lot 1",
                    "product_id": cls.product2.id,
                    "company_id": cls.env.company.id,
                },
                {
                    "name": "Product 2 Lot 2",
                    "product_id": cls.product2.id,
                    "company_id": cls.env.company.id,
                },
            ]
        )
        cls.product3_lot1, cls.product3_lot2 = cls.env["stock.production.lot"].create(
            [
                {
                    "name": "Product 3 Lot 1",
                    "product_id": cls.product3.id,
                    "company_id": cls.env.company.id,
                },
                {
                    "name": "Product 3 Lot 2",
                    "product_id": cls.product3.id,
                    "company_id": cls.env.company.id,
                },
            ]
        )
        cls.location_supplier = cls.env.ref("stock.stock_location_suppliers")
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls._do_stock_move(
            cls.product1,
            cls.product1_lot1,
            10,
            cls.location_supplier,
            cls.location_stock,
        )
        cls._do_stock_move(
            cls.product1,
            cls.product1_lot2,
            10,
            cls.location_supplier,
            cls.location_stock,
        )
        # Product 2 Lot 1 manufactured from Product 1 Lot 1
        cls._do_manufacture_move(
            cls.product2,
            cls.product2_lot1,
            10,
            [(cls.product1, cls.product1_lot1, 10)],
        )
        # Product 2 Lot 2 manufactured from Product 2 Lot 2
        cls._do_manufacture_move(
            cls.product2,
            cls.product2_lot2,
            10,
            [(cls.product1, cls.product1_lot2, 10)],
        )
        # Product 3 Lot 1 manufactured from Product 2 Lot 1
        cls._do_manufacture_move(
            cls.product3,
            cls.product3_lot1,
            10,
            [(cls.product2, cls.product2_lot1, 10)],
        )
        # Product 3 Lot 2 manufactured from Product 2 Lot 2
        cls._do_manufacture_move(
            cls.product3,
            cls.product3_lot2,
            10,
            [(cls.product2, cls.product2_lot2, 10)],
        )

    @classmethod
    def _do_stock_move(
        cls, product, lot, qty, location_from, location_dest, validate=True
    ):
        move = cls.env["stock.move"].create(
            {
                "name": product.name,
                "product_id": product.id,
                "product_uom_qty": qty,
                "product_uom": product.uom_id.id,
                "location_id": location_from.id,
                "location_dest_id": location_dest.id,
                "move_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_id": product.uom_id.id,
                            "qty_done": qty,
                            "lot_id": lot.id,
                            "location_id": location_from.id,
                            "location_dest_id": location_dest.id,
                        },
                    )
                ],
            }
        )
        if validate:
            move._action_confirm()
            move._action_done()
        return move

    @classmethod
    def _do_manufacture_move(cls, product, lot, qty, consume_data, validate=True):
        assert isinstance(consume_data, list)
        # Consume data is a list of tuples (product, lot, qty)
        consume_moves = cls.env["stock.move"]
        for consume_product, consume_lot, consume_qty in consume_data:
            consume_moves += cls._do_stock_move(
                consume_product,
                consume_lot,
                consume_qty,
                cls.location_stock,
                product.property_stock_production,
                validate=validate,
            )
        # Do the actual production
        move = cls._do_stock_move(
            product,
            lot,
            qty,
            product.property_stock_production,
            cls.location_stock,
            validate=validate,
        )
        move.move_line_ids.consume_line_ids = [
            (6, 0, consume_moves.mapped("move_line_ids").ids)
        ]
        return move + consume_moves
