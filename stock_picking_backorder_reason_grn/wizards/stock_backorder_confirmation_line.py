# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockBackorderConfirmation(models.TransientModel):

    _inherit = "stock.backorder.confirmation.line"

    keep_grn = fields.Boolean()
