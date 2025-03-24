# Copyright 2023-2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models


class ProductSetLine(models.Model):
    _inherit = "product.set.line"

    def prepare_picking_stock_move_values(self, picking, quantity):
        self.ensure_one()
        product = self.product_id.with_context(
            lang=picking.partner_id.lang or self.env.user.lang
        )
        # Inspired in the _prepare_stock_move_vals() method of purchase_stock
        return {
            # truncate to 2000 to avoid triggering index limit error
            "name": (self.product_id.display_name or "")[:2000],
            "product_id": self.product_id.id,
            "location_id": picking.location_id.id,
            "location_dest_id": picking.location_dest_id.id,
            "picking_id": picking.id,
            "partner_id": picking.partner_id.id,
            "state": "draft",
            "company_id": picking.company_id.id,
            "picking_type_id": picking.picking_type_id.id,
            "group_id": picking.group_id.id,
            "description_picking": product.description_pickingin,
            "warehouse_id": picking.picking_type_id.warehouse_id.id,
            "product_uom_qty": self.quantity * quantity,
            "product_uom": self.product_id.uom_id.id,
            "sequence": self.sequence,
        }
