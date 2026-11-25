# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPackage(models.Model):
    _inherit = "stock.package"

    # Note: package_dest_id is now built into stock.package in Odoo 19.0
    # No custom field definition needed


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    # Add package_dest_id as related field for move lines
    package_dest_id = fields.Many2one(
        related="package_id.package_dest_id",
        string="Destination Package",
        readonly=False,
        store=True,
    )
