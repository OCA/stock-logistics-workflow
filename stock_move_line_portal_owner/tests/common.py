from odoo import Command
from odoo.tests import HttpCase, TransactionCase


class StockMoveLinePortalDataMixin:
    @classmethod
    def _create_product(cls, name, code):
        return cls.env["product.product"].create(
            {
                "name": name,
                "default_code": code,
                "detailed_type": "product",
            }
        )

    @classmethod
    def _create_picking_with_move(
        cls, partner, picking_type, location_src, location_dest, product, qty
    ):
        picking = cls.env["stock.picking"].create(
            {
                "partner_id": partner.id,
                "picking_type_id": picking_type.id,
                "location_id": location_src.id,
                "location_dest_id": location_dest.id,
            }
        )
        move = cls.env["stock.move"].create(
            {
                "name": product.name,
                "product_id": product.id,
                "product_uom_qty": qty,
                "product_uom": product.uom_id.id,
                "picking_id": picking.id,
                "location_id": location_src.id,
                "location_dest_id": location_dest.id,
            }
        )
        picking.action_confirm()

        move.move_line_ids.unlink()
        move_line = cls.env["stock.move.line"].create(
            {
                "picking_id": picking.id,
                "move_id": move.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "quantity": qty,
                "location_id": location_src.id,
                "location_dest_id": location_dest.id,
                "owner_id": partner.id,
            }
        )
        return picking, move_line

    @classmethod
    def _create_move_line_portal_data(cls):
        cls.company = cls.env.company

        cls.partner_a = cls.env["res.partner"].create({"name": "Portal Partner A"})
        cls.partner_b = cls.env["res.partner"].create({"name": "Portal Partner B"})

        portal_group = cls.env.ref("base.group_portal")
        cls.portal_user_a = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Portal User A",
                    "login": "portal_a",
                    "password": "portal_a",
                    "partner_id": cls.partner_a.id,
                    "groups_id": [Command.set([portal_group.id])],
                }
            )
        )
        cls.portal_user_b = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Portal User B",
                    "login": "portal_b",
                    "password": "portal_b",
                    "partner_id": cls.partner_b.id,
                    "groups_id": [Command.set([portal_group.id])],
                }
            )
        )

        cls.product_1 = cls._create_product("Producto ML 1", "ML-01")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = (
            cls.env["stock.warehouse"]
            .search([("company_id", "=", cls.company.id)], limit=1)
            .lot_stock_id
        )

        cls.receipt_type = cls.env["stock.picking.type"].search(
            [("code", "=", "incoming"), ("company_id", "=", cls.company.id)], limit=1
        )
        cls.delivery_type = cls.env["stock.picking.type"].search(
            [("code", "=", "outgoing"), ("company_id", "=", cls.company.id)], limit=1
        )

        cls.picking_in_a, cls.move_line_in_a = cls._create_picking_with_move(
            cls.partner_a,
            cls.receipt_type,
            cls.supplier_location,
            cls.stock_location,
            cls.product_1,
            10,
        )
        cls.picking_out_a, cls.move_line_out_a = cls._create_picking_with_move(
            cls.partner_a,
            cls.delivery_type,
            cls.stock_location,
            cls.customer_location,
            cls.product_1,
            5,
        )

        cls.picking_in_b, cls.move_line_in_b = cls._create_picking_with_move(
            cls.partner_b,
            cls.receipt_type,
            cls.supplier_location,
            cls.stock_location,
            cls.product_1,
            20,
        )


class StockMoveLinePortalCommon(StockMoveLinePortalDataMixin, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._create_move_line_portal_data()


class StockMoveLinePortalHttpCommon(StockMoveLinePortalDataMixin, HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._create_move_line_portal_data()
