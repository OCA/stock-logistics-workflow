# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        values = super()._get_new_picking_values()
        carrier = self.group_id.carrier_id
        if carrier and self.picking_type_id.code in ["outgoing", "incoming"]:
            values["carrier_id"] = carrier.id
        return values
