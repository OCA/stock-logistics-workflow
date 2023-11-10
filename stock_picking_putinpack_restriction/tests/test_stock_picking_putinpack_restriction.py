# Copyright 2023 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestStockPickingPutInPackRestriction(SavepointCase):
    @classmethod
    def setUpClass(cls):
        """ """
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "product",
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
            "picking_type_id": cls.picking_type.id,
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

    def test_put_in_pack_package_not_allowed(self):
        """Check put in pack is not allowed with no_package."""
        picking_type = self.picking.picking_type_id
        picking_type.put_in_pack_restriction = "no_package"
        msg = (
            "Destination package can not be used with %s transfer." % picking_type.name
        )
        with self.assertRaisesRegex(ValidationError, msg):
            self.picking.action_put_in_pack()

    def test_picking_done_breaks_restriction_with_package(self):
        self.picking_type.put_in_pack_restriction = "with_package"
        self.picking.action_assign()
        self.assertEqual(self.picking.state, "assigned")
        self.picking.move_line_ids[0].qty_done = 5.0
        msg = "A package is required for transfer type %s." % self.picking_type.name
        with self.assertRaisesRegex(ValidationError, msg):
            self.picking._action_done()
        # Check it works without restriction
        self.picking_type.put_in_pack_restriction = False
        self.picking._action_done()
        self.assertEqual(self.picking.state, "done")

    def test_picking_done_breaks_restriction_no_package(self):
        self.picking_type.put_in_pack_restriction = "no_package"
        self.picking.action_assign()
        self.assertEqual(self.picking.state, "assigned")
        self.picking.move_line_ids[0].qty_done = 5.0
        self.picking.move_line_ids[0].result_package_id = self.env[
            "stock.quant.package"
        ].create({})
        msg = (
            "Using a package on transfer type %s is not allowed."
            % self.picking_type.name
        )
        with self.assertRaisesRegex(ValidationError, msg):
            self.picking._action_done()
        # Check it works without restriction
        self.picking_type.put_in_pack_restriction = False
        self.picking._action_done()
        self.assertEqual(self.picking.state, "done")
