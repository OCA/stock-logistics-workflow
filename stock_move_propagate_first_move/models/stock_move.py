# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    first_move_id = fields.Many2one(
        comodel_name="stock.move",
        string="First Move",
        readonly=True,
        help="The original move which generated this one.",
    )
    first_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Original Operation Type",
        related="first_move_id.picking_type_id",
        store=True,
        help="Picking type of the original move which generated this one.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if not rec.first_move_id:
                rec.first_move_id = rec
        return records
