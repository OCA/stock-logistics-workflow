# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    disable_unassign_lots_to_remove = fields.Boolean(
        string="Disable Unassign Lots to Remove",
        help="If checked, the unassignment of lots to remove will be disabled "
        "for this picking type. This is useful for picking types that "
        "should not allow unassigning lots, such as those used for "
        "expired lot removal.",
    )
