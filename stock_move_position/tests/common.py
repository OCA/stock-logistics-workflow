# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from unittest.mock import patch

from odoo.fields import Command
from odoo.tests import TransactionCase


class StockMovePositionCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Products and operation types used by the tests."""
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Number with the default step, whatever other modules configure
        cls.startClassPatcher(
            patch.object(type(cls.env["stock.picking"]), "_line_numbering_step", 1)
        )
        cls.product = cls._create_product("Test product", "TEST")
        cls.product_2 = cls._create_product("Test product 2", "TEST2")
        cls.out_type = cls.env.ref("stock.picking_type_out")
        cls.in_type = cls.env.ref("stock.picking_type_in")
        cls.out_dest = cls.out_type.default_location_dest_id

    @classmethod
    def _create_product(cls, name, code):
        """Create a storable product."""
        return cls.env["product.product"].create(
            {
                "name": name,
                "default_code": code,
                "type": "consu",
                "is_storable": True,
                "list_price": 10.0,
            }
        )

    @classmethod
    def _create_picking(cls, picking_type, lines_spec):
        """Create a transfer with one move per (product, qty) spec."""
        src = picking_type.default_location_src_id
        dest = picking_type.default_location_dest_id
        return cls.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": src.id,
                "location_dest_id": dest.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": line_spec[0].id,
                            "product_uom_qty": line_spec[1],
                            "product_uom": line_spec[0].uom_id.id,
                            "location_id": src.id,
                            "location_dest_id": dest.id,
                        }
                    )
                    for line_spec in lines_spec
                ],
            }
        )
