# 2020 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# @author Jordi Ballester <jordi.ballester@forgeflow.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


class StockValuationLayerUsage(models.Model):
    _name = "stock.valuation.layer.usage"
    _description = "Stock Valuation Layer Usage"

    product_id = fields.Many2one(
        comodel_name="product.product",
        related="stock_valuation_layer_id.product_id",
        store=True,
    )
    stock_valuation_layer_id = fields.Many2one(
        comodel_name="stock.valuation.layer",
        string="Stock Valuation Layer",
        help="Valuation Layer that was used",
        required=True,
    )
    dest_stock_valuation_layer_id = fields.Many2one(
        comodel_name="stock.valuation.layer",
        string="Destination Stock Valuation Layer",
        help="Valuation Layer that was used",
        required=False,
    )
    company_id = fields.Many2one("res.company", "Company", readonly=True, required=True)
    stock_move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Stock Move",
        help="Stock move that took the quantities and value from the layer",
    )
    quantity = fields.Float(string="Taken Quantity")
    value = fields.Float(string="Taken Value")

    def init(self):
        tools.create_index(
            self._cr,
            "stock_valuation_layer_usage_index",
            self._table,
            ["stock_valuation_layer_id", "stock_move_id", "stock_move_id"],
        )

    @api.constrains(
        "stock_valuation_layer_id",
        "dest_stock_valuation_layer_id",
    )
    def _check_same_layer(self):
        for rec in self:
            if (
                rec.dest_stock_valuation_layer_id
                and rec.dest_stock_valuation_layer_id
                and rec.dest_stock_valuation_layer_id.id
                == rec.stock_valuation_layer_id.id
            ):
                raise ValidationError(
                    _("You can't user same layer as origin and destination")
                )
