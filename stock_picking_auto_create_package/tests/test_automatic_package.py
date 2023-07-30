# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestAutomaticPackage(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "product",
            }
        )
        cls.product_packaging = cls.env["product.packaging"].create(
            {
                "name": "Box",
                "qty": "2",
                "product_id": cls.product.id,
            }
        )
        cls.product_delivery = cls.env["product.product"].create(
            {
                "name": "Delivery Test",
                "type": "service",
            }
        )
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.env["stock.quant"]._update_available_quantity(
            cls.product,
            cls.stock,
            10,
        )
        cls.picking = cls._create_picking()
        cls.picking.move_lines.update({"quantity_done": 4.0})

    @classmethod
    def _create_picking(cls):
        vals = {
            "location_id": cls.stock.id,
            "location_dest_id": cls.customers.id,
            "picking_type_id": cls.env.ref("stock.picking_type_out").id,
            "move_lines": [
                (
                    0,
                    0,
                    {
                        "name": "Product Test",
                        "location_id": cls.stock.id,
                        "location_dest_id": cls.customers.id,
                        "product_id": cls.product.id,
                        "product_uom_qty": 5.0,
                        "product_uom": cls.product.uom_id.id,
                    },
                )
            ],
        }
        return cls.env["stock.picking"].create(vals)

    def test_automatic_no(self):
        """
        Disable the automatic package creation
        Create a picking, fill in quantities and validate it
        The move line should not contain a package
        """
        self.picking.picking_type_id.automatic_package_creation_mode = False
        self.picking._action_done()
        self.assertFalse(self.picking.move_line_ids.result_package_id)

    def test_automatic_single(self):
        """
        Enable the automatic package creation with mode "single"
        Create a picking, fill in quantities and validate it
        The move line should contain a package
        """
        self.picking.picking_type_id.automatic_package_creation_mode = "single"
        self.picking._action_done()
        self.assertTrue(self.picking.move_line_ids.result_package_id)
        self.assertTrue(len(self.picking.move_line_ids.result_package_id), 1)

    def test_automatic_packaging(self):
        """
        Enable the automatic package creation with mode "packaging"
        Create a picking, fill in quantities and validate it
        The move line should contain a package per product packaging
        """
        self.picking.picking_type_id.automatic_package_creation_mode = "packaging"
        self.picking._action_done()
        self.assertTrue(self.picking.move_line_ids.result_package_id)
        self.assertTrue(len(self.picking.move_line_ids.result_package_id), 2)
