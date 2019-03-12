# © 2019 Today Akretion
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    move_ids = fields.One2many(
        string="Stock Moves",
        comodel_name="stock.move",
        inverse_name="product_id",
        help="Technical: used to compute quantities to pick.",
    )

    @api.depends("move_ids")
    def _compute_process_qty(self):
        res = super(ProductProduct, self)._compute_process_qty()
        if self.env.context["parent_model"] == "stock.picking":
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

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.context.get("in_current_parent"):
            picking = self.env["stock.picking"].browse(
                self.env.context.get("parent_id")
            )
            if picking:
                moves = self.env["stock.move"].search(
                    [("picking_id", "=", picking.id)]
                )
                args.append((("id", "in", moves.mapped("product_id").ids)))
        return super(ProductProduct, self).search(
            args, offset=offset, limit=limit, order=order, count=count
        )
