# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockValuationLayer(models.Model):

    _inherit = "stock.valuation.layer"

    categ_id = fields.Many2one(store=True)
