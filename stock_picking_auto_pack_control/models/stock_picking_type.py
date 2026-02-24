# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    auto_pack_requires_packaging = fields.Boolean(
        help="If enabled, automatic package creation will "
        "only apply to products that have packaging defined.",
    )
