# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _search_picking_for_assignation(self):
        # totally reimplement this one to add a hook to change the domain
        self.ensure_one()
        return self.env["stock.picking"].search(
            self._domain_search_picking_for_assignation(), limit=1
        )

    def _domain_search_picking_for_assignation(self):
        return self._domain_search_picking_for_assignation_default()

    def _domain_search_picking_for_assignation_default(self):
        return [
            ("group_id", "=", self.group_id.id),
            ("location_id", "=", self.location_id.id),
            ("location_dest_id", "=", self.location_dest_id.id),
            ("picking_type_id", "=", self.picking_type_id.id),
            ("printed", "=", False),
            ("immediate_transfer", "=", False),
            (
                "state",
                "in",
                ["draft", "confirmed", "waiting", "partially_available", "assigned"],
            ),
        ]
