# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        vals = super()._get_new_picking_values()
        if not vals.get("carrier_id"):
            rule_carrier = self.rule_id.partner_address_id.property_delivery_carrier_id
            if rule_carrier:
                vals["carrier_id"] = rule_carrier.id
        return vals
