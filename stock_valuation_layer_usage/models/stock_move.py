# 2020 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# @author Jordi Ballester <jordi.ballester@forgeflow.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    layer_usage_ids = fields.One2many(
        comodel_name="stock.valuation.layer.usage",
        inverse_name="stock_move_id",
        string="Valuation Layer Usage",
        help="Trace what valuation layers have been used by this move, "
        "including the quantities taken.",
    )

    def _create_out_svl(self, forced_quantity=None):
        layers = self.env["stock.valuation.layer"]
        for move in self:
            move = move.with_context(used_in_move_id=move.id)
            layer = super(StockMove, move)._create_out_svl(
                forced_quantity=forced_quantity
            )
            layers |= layer
        return layers

    def _create_dropshipped_svl(self, forced_quantity=None):
        layers = super(StockMove, self)._create_dropshipped_svl(
            forced_quantity=forced_quantity
        )
        for move in self:
            in_layer = layers.filtered(
                lambda l: l.quantity > 0 and l.stock_move_id == move
            )
            self.env["stock.valuation.layer.usage"].sudo().create(
                {
                    "stock_valuation_layer_id": in_layer.id,
                    "stock_move_id": move.id,
                    "quantity": in_layer.quantity,
                    "value": in_layer.value,
                    "company_id": in_layer.company_id.id,
                }
            )
        return layers
