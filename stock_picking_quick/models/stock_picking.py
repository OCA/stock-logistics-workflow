# © 2019 Today Akretion
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "product.mass.addition"]

    @api.multi
    def add_product(self):
        self.ensure_one()
        res = self._common_action_keys()
        res["context"].update(
            {
                "search_default_consumable": 1,
                "search_default_filter_to_pick": 1,
                "search_default_filter_for_current_location": 1,
                "location": [self.location_id.id],
            }
        )
        res["name"] = "🔙 %s" % (_("Product Variants"))
        res["view_id"] = (
            self.env.ref("stock_picking_quick.product_tree_view4picking").id,
        )
        res["search_view_id"] = (
            self.env.ref("stock_picking_quick.product_search_view4picking").id,
        )
        return res

    def _prepare_quick_line(self, product):
        res = super(StockPicking, self)._prepare_quick_line(product)
        res["location_id"] = self.location_id.id
        res["location_dest_id"] = self.location_dest_id.id
        return res

    def _get_quick_line(self, product):
        return self.env["stock.move"].search(
            [("product_id", "=", product.id), ("picking_id", "=", self.id)],
            limit=1,
        )

    def _get_quick_line_qty_vals(self, product):
        return {"product_uom_qty": product.qty_to_process}

    def _complete_quick_line_vals(self, vals, lines_key=""):
        return super(StockPicking, self)._complete_quick_line_vals(
            vals, lines_key="move_ids_without_package"
        )

    def _add_quick_line(self, product, lines_key=""):
        return super(StockPicking, self)._add_quick_line(
            product, lines_key="move_ids_without_package"
        )
