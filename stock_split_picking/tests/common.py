# Copyright 2017 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2018 Camptocamp SA - Julien Coux
# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestStockSplitPickingCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))

        cls.src_location = cls.env.ref("stock.stock_location_stock")
        cls.dest_location = cls.env.ref("stock.stock_location_customers")

        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "consu", "is_storable": True}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Test product 2", "type": "consu", "is_storable": True}
        )
        cls.product_consu = cls.env["product.product"].create(
            {"name": "Test product", "type": "consu"}
        )
        cls.product_consu_2 = cls.env["product.product"].create(
            {"name": "Test product 2", "type": "consu"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.picking = cls._create_picking()
        cls.move = cls._create_stock_move(cls.product, cls.picking)
        cls.move_2 = cls._create_stock_move(cls.product_2, cls.picking)
        cls.picking_consu = cls._create_picking()
        cls.move_consu = cls._create_stock_move(cls.product_consu, cls.picking_consu)
        cls.move_consu_2 = cls._create_stock_move(
            cls.product_consu_2, cls.picking_consu
        )

    @classmethod
    def _create_picking(cls):
        return cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.src_location.id,
                "location_dest_id": cls.dest_location.id,
            }
        )

    @classmethod
    def _create_stock_move(cls, product, picking, qty=10):
        return cls.env["stock.move"].create(
            {
                "name": "/",
                "picking_id": picking.id,
                "product_id": product.id,
                "product_uom_qty": qty,
                "product_uom": product.uom_id.id,
                "location_id": cls.src_location.id,
                "location_dest_id": cls.dest_location.id,
            }
        )

    @classmethod
    def _split_picking(cls, picking, **wizard_vals):
        return (
            cls.env["stock.split.picking"]
            .with_context(active_ids=picking.ids)
            .create(wizard_vals)
            .action_apply()
        )
