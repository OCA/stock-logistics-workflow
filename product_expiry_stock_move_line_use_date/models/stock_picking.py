# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    has_use_date_text = fields.Boolean(compute='_compute_has_use_date_text')

    @api.depends('move_lines', 'move_lines.show_lots_use_date_text')
    def _compute_has_use_date_text(self):
        for picking in self:
            picking.has_use_date_text = any(
                m.show_lots_use_date_text for m in picking.move_lines
            )
