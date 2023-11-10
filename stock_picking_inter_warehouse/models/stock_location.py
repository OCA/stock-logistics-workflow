# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    inter_warehouse_partner_id = fields.One2many(
        "res.partner", "default_stock_location_src_id"
    )
