# 2026 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError


class StockMoveValuationUsage(models.Model):
    _name = "stock.move.valuation.usage"
    _description = "Stock Move Valuation Usage"

    product_id = fields.Many2one(
        comodel_name="product.product",
        related="dest_stock_move_id.product_id",
        store=True,
    )
    src_stock_move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Source Stock Move",
        help="Incoming stock move that was used as a source for valuation",
    )
    dest_stock_move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Destination Stock Move",
        help="Outgoing stock move that consumed from the source move",
        required=False,
    )
    company_id = fields.Many2one("res.company", "Company", readonly=True, required=True)
    quantity = fields.Float(string="Taken Quantity")
    value = fields.Float(string="Taken Value")

    def init(self):
        tools.create_index(
            self.env.cr,
            "stock_move_valuation_usage_index",
            self._table,
            ["src_stock_move_id", "dest_stock_move_id"],
        )

    @api.constrains("src_stock_move_id", "dest_stock_move_id")
    def _check_same_move(self):
        for rec in self:
            if (
                rec.dest_stock_move_id
                and rec.src_stock_move_id
                and rec.dest_stock_move_id == rec.src_stock_move_id
                and not rec.src_stock_move_id.is_dropship
            ):
                raise ValidationError(
                    self.env._("You can't use same move as origin and destination")
                )
