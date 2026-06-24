# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class ReservationPolicyCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_unit = cls.quick_ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
                "uom_id": cls.uom_unit.id,
            }
        )
        cls.warehouse = cls.quick_ref("stock.warehouse0")
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.customer_location = cls.quick_ref("stock.stock_location_customers")
        cls.picking_type_out = cls.warehouse.out_type_id

    @classmethod
    def _set_stock(cls, qty, product=None, location=None):
        """Add ``qty`` of available quantity (starting from an empty stock)."""
        cls.env["stock.quant"]._update_available_quantity(
            product or cls.product, location or cls.stock_location, qty
        )

    def _create_picking(self, qty, reservation_policy=None, product=None):
        """Create an outgoing transfer with a single move (not yet confirmed)."""
        product = product or self.product
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        self.env["stock.move"].create(
            {
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": qty,
                "picking_id": picking.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        if reservation_policy:
            picking.reservation_policy = reservation_policy
        return picking
