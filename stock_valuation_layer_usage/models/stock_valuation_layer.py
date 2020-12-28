# 2020 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# @author Jordi Ballester <jordi.ballester@forgeflow.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    usage_ids = fields.One2many(
        comodel_name="stock.valuation.layer.usage",
        inverse_name="stock_valuation_layer_id",
        string="Valuation Usage",
        help="Trace on what stock moves has the stock valuation been used in, "
        "including the quantities taken.",
    )
