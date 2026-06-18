# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockMove(models.Model):

    _inherit = "stock.picking.type"

    can_reassign = fields.Boolean(
        help="Check this if you want to allow moves reassignation."
    )
    default_move_reassign_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        help="This is the default operation type that welcome the reassigned products.",
    )
    default_move_reassign_transfer_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
    )
