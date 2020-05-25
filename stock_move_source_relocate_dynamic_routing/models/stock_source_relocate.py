# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class StockSourceRelocate(models.Model):

    _inherit = "stock.source.relocate"

    def action_view_dynamic_routing(self):
        picking_types = self.mapped("picking_type_id")
        routing = self.env["stock.routing"].search(
            [("picking_type_id", "in", picking_types.ids)]
        )
        context = self.env.context
        if len(picking_types) == 1:
            context = dict(context, default_picking_type_id=picking_types.id)
        return {
            "name": _("Dynamic Routing"),
            "domain": [("id", "in", routing.ids)],
            "res_model": "stock.routing",
            "type": "ir.actions.act_window",
            "view_id": False,
            "view_mode": "tree,form",
            "limit": 20,
            "context": context,
        }
