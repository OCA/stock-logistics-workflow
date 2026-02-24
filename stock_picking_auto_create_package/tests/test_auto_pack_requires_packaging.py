# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestAutoPackRequiresPackaging(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.package = cls.env["uom.uom"].create(
            {
                "name": "Pack of 6",
                "relative_factor": 6.0,
                "relative_uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Packaged Product",
                "type": "consu",
                "is_storable": True,
                "uom_ids": cls.package,
            }
        )

        cls.picking_type = cls.env["stock.picking.type"].create(
            {
                "name": "Test Packing",
                "code": "outgoing",
                "sequence_code": "TP",
                "warehouse_id": cls.env["stock.warehouse"].search([], limit=1).id,
                "automatic_package_creation_mode": "packaging",
            }
        )

        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

    def _create_picking(
        self, partner, picking_type, location, location_dest, product, product_qty
    ):
        picking = self.env["stock.picking"].create(
            {
                "partner_id": partner.id,
                "picking_type_id": picking_type.id,
                "location_id": location.id,
                "location_dest_id": location_dest.id,
                "move_ids": [
                    Command.create(
                        {
                            "reference": product.name,
                            "product_id": product.id,
                            "product_uom_qty": product_qty,
                            "product_uom": product.uom_id.id,
                            "location_id": location.id,
                            "location_dest_id": location_dest.id,
                        }
                    )
                ],
            }
        )
        return picking

    def test_01_auto_pack_packages_workflow(self):
        """Test the workflow of automatic package creation based
        on packaging requirements."""
        picking = self._create_picking(
            self.partner,
            self.picking_type,
            self.stock_location,
            self.customer_location,
            self.product,
            60.0,
        )
        # Case 1: A product has a package assigned and auto_pack_requires_packaging
        # is False -> Should apply the behaviour defined in
        # stock_picking_auto_create_package
        picking.button_validate()
        # There should be 10 different packages (60/6)
        self.assertEqual(len(picking.move_ids.package_ids), 10)

        # Case 2. A product has a package assigned and auto_pack_requires_packaging
        # is True -> Should apply the same behaviour as Case 1
        picking = self._create_picking(
            self.partner,
            self.picking_type,
            self.stock_location,
            self.customer_location,
            self.product,
            60.0,
        )
        self.picking_type.auto_pack_requires_packaging = True
        picking.button_validate()
        # There should be 10 different packages (60/6)
        self.assertEqual(len(picking.move_ids.package_ids), 10)

        # Case 3. A product has no packages assigned and auto_pack_requires_packaging
        # is True -> Should not assign any packages
        self.product.write(
            {
                "uom_ids": [Command.clear()],
            }
        )
        picking = self._create_picking(
            self.partner,
            self.picking_type,
            self.stock_location,
            self.customer_location,
            self.product,
            60.0,
        )
        picking.button_validate()
        self.assertEqual(len(picking.move_ids.package_ids), 0)

        # Case 4. A product has no packages assigned and auto_pack_requires_packaging
        # is False -> Should apply the behaviour in the
        # stock_picking_auto_create_package module
        self.picking_type.auto_pack_requires_packaging = False
        picking = self._create_picking(
            self.partner,
            self.picking_type,
            self.stock_location,
            self.customer_location,
            self.product,
            60.0,
        )
        picking.button_validate()
        # There should be 60 different packages (qty 1 per package)
        self.assertEqual(len(picking.move_ids.package_ids), 60)
