# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockRoute(models.Model):
    _inherit = "stock.route"

    allow_quant_lock = fields.Boolean(
        string="Allow quant lock",
        help="If checked, this route can be used to lock stock quants. "
        "The lock transfer is created by the pull rule of this route whose "
        "source location contains the location of the quant to lock.",
    )
