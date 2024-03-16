# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    group_pickings_by_customer = fields.Boolean(
        help="If checked, and if the 'Group pickings' option is set, pickings with"
        "the same customer will be merged."
    )
