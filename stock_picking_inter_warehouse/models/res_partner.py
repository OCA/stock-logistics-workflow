# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    default_stock_location_src_id = fields.Many2one(
        "stock.location", "Default Source Location"
    )
