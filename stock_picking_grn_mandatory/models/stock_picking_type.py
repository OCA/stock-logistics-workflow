# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    is_grn_mandatory = fields.Boolean(
        help="Check this if you want user to fill in the GRN field for pickings"
        " of this type."
    )
