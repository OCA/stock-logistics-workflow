# Copyright 2024 Tecnativa S.L. - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _should_bypass_reservation(self, forced_location=False):
        if self.picking_type_id.force_reservation:
            return False
        return super()._should_bypass_reservation()
