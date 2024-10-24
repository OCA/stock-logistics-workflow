# 2024 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class QuantPackage(models.Model):
    _inherit = "stock.quant.package"

    disposable_used = fields.Boolean(
        help="The disposable package has been used in a delivery",
        default=False,
    )
