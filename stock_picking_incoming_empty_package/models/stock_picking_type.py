# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    empty_package_at_validation = fields.Boolean()
