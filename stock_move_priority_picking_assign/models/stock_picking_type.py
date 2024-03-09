# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    group_moves_per_priority = fields.Boolean(
        help="Check this if you want to group moves per priority when creating"
        "pickings during move assignation."
    )
