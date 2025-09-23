# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        # OVERRIDE to propagate the carrier, depending on the dynamic routing rule
        # configuration.
        vals = super()._get_new_picking_values()
        if (
            (routing_rule := self.env.context.get("__routing_rule"))
            and routing_rule.propagate_carrier
            and self.group_id.carrier_id
        ):
            vals["carrier_id"] = self.group_id.carrier_id.id
        return vals
