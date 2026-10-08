from collections import defaultdict

from odoo import models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "product.catalog.mixin"]

    def action_add_from_catalog(self):
        self.ensure_one()
        return super().action_add_from_catalog()

    def _get_product_catalog_domain(self):
        self.ensure_one()
        return super()._get_product_catalog_domain()

    def _get_action_add_from_catalog_extra_context(self):
        self.ensure_one()

        res = super()._get_action_add_from_catalog_extra_context()

        res.update(
            {
                "order_id": self.id,
                "search_default_consumable": 1,
                "search_default_filter_to_pick": 1,
                "search_default_filter_for_current_location": 1,
                "location": [self.location_id.id],
            }
        )

        return res

    def _get_product_catalog_record_lines(
        self,
        product_ids,
        *,
        section_id=None,
        **kwargs,
    ):
        self.ensure_one()

        grouped_lines = defaultdict(lambda: self.env["stock.move"])

        for move in self.move_ids_without_package:
            if move.product_id.id in product_ids:
                grouped_lines[move.product_id] |= move

        return grouped_lines

    def _get_product_catalog_order_data(self, products, **kwargs):
        return {
            product.id: {
                "price": product.standard_price,
                "productType": product.type,
            }
            for product in products
        }

    def _update_order_line_info(
        self,
        product_id,
        quantity,
        *,
        child_field="move_ids_without_package",
        **kwargs,
    ):
        self.ensure_one()

        move = self.move_ids_without_package.filtered(
            lambda m: m.product_id.id == product_id
        )[:1]

        if move:
            if quantity:
                move.product_uom_qty = quantity
            else:
                move.unlink()

            return quantity

        if quantity <= 0:
            return 0

        product = self.env["product.product"].browse(product_id)

        self.env["stock.move"].create(
            {
                "name": product.display_name,
                "product_id": product.id,
                "product_uom_qty": quantity,
                "product_uom": product.uom_id.id,
                "picking_id": self.id,
                "location_id": self.location_id.id,
                "location_dest_id": self.location_dest_id.id,
                "company_id": self.company_id.id,
            }
        )

        return quantity
