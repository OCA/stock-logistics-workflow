# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase


class CommonStockPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.lot_obj = cls.env["stock.lot"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.company_1 = cls.env.ref("base.main_company")
        cls.company_2 = cls.env.ref("stock.res_company_1")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_in_2 = cls.env.ref("stock.chi_picking_type_in")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.supplier = cls.env["res.partner"].create({"name": "Supplier - test"})

        cls.stock_serial_sequence_2 = cls.env.ref(
            "stock.sequence_production_lots"
        ).copy()
        cls.stock_serial_sequence_2.prefix = "TEST"
        cls.company_2.stock_lot_serial_sequence_id = cls.stock_serial_sequence_2.id

    @classmethod
    def _create_product(
        cls, tracking="lot", auto=True, every_n=0, multiple_allow=False
    ):
        """
        Create a new product and set the following properties:

        Args:
            tracking (str): Tracking method
            auto (bool): Auto create lot
            every_n (int): Create lot every n units
            multiple_allow (bool): Allow multiple serial numbers

        Returns:
            product.product: Created product
        """
        name = "{tracking} - {auto}".format(tracking=tracking, auto=auto)
        return cls.env["product.product"].create(
            {
                "name": name,
                "type": "product",
                "tracking": tracking,
                "auto_create_lot": auto,
                "create_lot_every_n": every_n,
                "only_multiples_allowed": multiple_allow,
            }
        )

    @classmethod
    def _create_picking(cls, multicompany=False, immediate_transfer=False):
        """
        Create a new picking and set the following properties:

        Args:
            multicompany (bool): Create picking for a second company

        Returns:
            stock.picking: Created picking
        """
        company = cls.company_1 if not multicompany else cls.company_2
        picking_type_in = (
            cls.picking_type_in if not multicompany else cls.picking_type_in_2
        )
        cls.picking = (
            cls.env["stock.picking"]
            .with_context(
                default_picking_type_id=picking_type_in.id,
                default_immediate_transfer=immediate_transfer,
            )
            .with_company(company)
            .create(
                {
                    "partner_id": cls.supplier.id,
                    "picking_type_id": picking_type_in.id,
                    "location_id": cls.supplier_location.id,
                }
            )
        )

    @classmethod
    def _create_move(
        cls, product=None, qty=1.0, multicompany=False, immediate_transfer=False
    ):
        """Create a new stock move for the given product and quantity

        Args:
            product (product.product): Product. Defaults to None
            qty (float): Quantity. Defaults to 1.0.
            multicompany (bool): Create move for a second company. Defaults to False.

        """
        company = cls.company_1 if not multicompany else cls.company_2
        location_dest = cls.picking.picking_type_id.default_location_dest_id
        cls.move = (
            cls.env["stock.move"]
            .with_company(company)
            .create(
                {
                    "name": "test-{product}".format(product=product.name),
                    "product_id": product.id,
                    "picking_id": cls.picking.id,
                    "picking_type_id": cls.picking.picking_type_id.id,
                    "product_uom_qty": qty,
                    "product_uom": product.uom_id.id,
                    "location_id": cls.supplier_location.id,
                    "location_dest_id": location_dest.id,
                    "quantity_done": qty if immediate_transfer else 0,
                    "move_line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": product.id,
                                "reserved_uom_qty": qty,
                                "product_uom_id": product.uom_id.id,
                                "location_id": cls.supplier_location.id,
                                "location_dest_id": location_dest.id,
                                "picking_id": cls.picking.id,
                            },
                        )
                    ],
                }
            )
        )
