# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _compute_move_type(self):
        # pylint: disable=missing-return
        super()._compute_move_type()
        for record in self:
            if record.picking_type_id.force_move_type:
                record.move_type = record.picking_type_id.move_type
