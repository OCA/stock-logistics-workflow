# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    create_late_picking_activity = fields.Boolean(
        help="If checked, the pickings belonging to this 'operation "
             "type' will be checked periodically to request to update "
             "their planned date.",
    )
    late_picking_activity_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Late picking activity responsible",
    )
