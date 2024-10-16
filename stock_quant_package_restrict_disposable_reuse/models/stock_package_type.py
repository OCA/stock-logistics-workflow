# 2024 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class PackageType(models.Model):
    _inherit = "stock.package.type"

    restrict_reuse = fields.Boolean(
        string="Restrict reuse of disposables",
        help="Restrict the reuse of disposable packages when "
        "they have been already used in a delivery.",
    )
