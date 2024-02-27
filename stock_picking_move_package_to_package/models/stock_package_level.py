# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPackageLevel(models.Model):
    _inherit = "stock.package_level"

    package_dest_id = fields.Many2one(
        "stock.quant.package",
        "Destination Package",
        required=False,
        check_company=True,
        domain="[('location_id', 'child_of', parent.location_dest_id), "
        "'|', "
        "('company_id', '=', False), "
        "('company_id', '=', company_id)]",
    )
