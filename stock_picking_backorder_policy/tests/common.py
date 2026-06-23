# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class BackorderPolicyCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create product
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
                "uom_id": cls.quick_ref("uom.product_uom_unit").id,
            }
        )
        # Warehouse / operation type
        cls.warehouse = cls.quick_ref("stock.warehouse0")
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.customer_location = cls.quick_ref("stock.stock_location_customers")
        cls.picking_type_out = cls.warehouse.out_type_id
        # Ensure default create_backorder is 'ask'
        cls.picking_type_out.create_backorder = "ask"
        # Seed plenty of stock so deliveries can always be reserved
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.stock_location, 1000.0
        )
        # Base commercial partner (no policy by default)
        cls.commercial_partner = cls.env["res.partner"].create(
            {
                "name": "Test Commercial Partner",
                "is_company": True,
            }
        )
        # Delivery address (child of commercial)
        cls.delivery_partner = cls.env["res.partner"].create(
            {
                "name": "Test Delivery Address",
                "parent_id": cls.commercial_partner.id,
                "type": "delivery",
            }
        )

    def _set_qty_done(self, picking, qty):
        """Set qty_done (and picked=True) on all move lines to qty."""
        for ml in picking.move_line_ids:
            ml.quantity = qty
            if qty > 0:
                ml.picked = True
