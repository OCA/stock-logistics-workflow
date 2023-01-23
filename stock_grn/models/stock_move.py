# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    grn_id = fields.Many2one(
        related="picking_id.grn_id", readonly=True, ondelete="cascade", store=True
    )
