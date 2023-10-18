# © 2022 Today Akretion
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.depends("stock_move_ids")
    @api.depends_context("parent_model")
    def _compute_process_qty(self):
        res = super()._compute_process_qty()
        if self.env.context.get("parent_model", False) == "stock.picking":
            quantities = self.env["stock.move"].read_group(
                [
                    ("picking_id", "=", self.env.context.get("parent_id")),
                    ("product_id", "in", self.ids),
                ],
                ["product_id", "product_qty:sum"],
                ["product_id"],
            )
            for product in self:
                for qty in quantities:
                    if product.id == qty["product_id"][0]:
                        product.qty_to_process = qty["product_qty"]
        return res

    def _default_quick_uom_id(self):
        if self.env.context.get("parent_model", False) == "stock.picking":
            return self.uom_id
        return super()._default_quick_uom_id()

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.context.get("in_current_parent"):
            picking = self.env["stock.picking"].browse(
                self.env.context.get("parent_id")
            )
            if picking:
                args.append(("stock_move_ids.picking_id", "=", picking.id))
        return super().search(
            args, offset=offset, limit=limit, order=order, count=count
        )
