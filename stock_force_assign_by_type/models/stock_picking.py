# Copyright 2024 Tecnativa S.L. - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    picking_type_force_reservation = fields.Boolean(
        related="picking_type_id.force_reservation"
    )
