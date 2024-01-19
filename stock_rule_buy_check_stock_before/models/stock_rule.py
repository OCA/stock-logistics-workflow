# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    disable_if_stock_exists = fields.Boolean(string="Bypass if stock exists")
