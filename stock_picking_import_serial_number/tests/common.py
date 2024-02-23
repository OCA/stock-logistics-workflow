# Copyright 2022 Tecnativa - Sergio Teruel
# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from base64 import b64encode
from os import path


class CommonStockPickingImportSerial(object):
    def assertUniqueIn(self, element_list):
        elements = []
        for element in element_list:
            if element in elements:
                raise Exception("Element %s is not unique in list" % element)
            elements.append(element)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.lot_obj = cls.env["stock.lot"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_in.use_create_lots = True
        cls.picking_type_in.show_reserved = True
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.supplier = cls.env["res.partner"].create({"name": "Supplier - test"})

    def _data_file(self, filename):
        with open(path.join(path.dirname(__file__), filename), "rb") as file:
            return b64encode(file.read())

    @classmethod
    def _create_product(cls, tracking="lot", reference=None):
        name = "{tracking}".format(tracking=tracking)
        vals = {
            "name": name,
            "type": "product",
            "tracking": tracking,
        }
        if reference:
            vals["default_code"] = reference
        return cls.env["product.product"].create(vals)

    @classmethod
    def _create_picking(cls):
        return (
            cls.env["stock.picking"]
            .with_context(default_picking_type_id=cls.picking_type_in.id)
            .create(
                {
                    "partner_id": cls.supplier.id,
                    "picking_type_id": cls.picking_type_in.id,
                    "location_id": cls.supplier_location.id,
                }
            )
        )

    @classmethod
    def _create_move(cls, picking, product=None, qty=1.0):
        location_dest = picking.picking_type_id.default_location_dest_id
        cls.move = cls.env["stock.move"].create(
            {
                "name": "test-{product}".format(product=product.name),
                "product_id": product.id,
                "picking_id": picking.id,
                "picking_type_id": picking.picking_type_id.id,
                "product_uom_qty": qty,
                "product_uom": product.uom_id.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": location_dest.id,
            }
        )
