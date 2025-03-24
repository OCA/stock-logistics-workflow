# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _should_bypass_reservation(self, forced_location=False):
        res = super()._should_bypass_reservation(forced_location=forced_location)
        return res or self.picking_type_id.bypass_reservation
