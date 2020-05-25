# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class StockRouting(models.Model):

    _inherit = "stock.routing"

    def action_view_source_relocate(self):
        picking_types = self.mapped("picking_type_id")
        routing = self.env["stock.routing"].search(
            [("picking_type_id", "in", picking_types.ids)]
        )
        context = self.env.context
        if len(picking_types) == 1:
            context = dict(context, default_picking_type_id=picking_types.id)
        return {
            "name": _("Source Relocation"),
            "domain": [("id", "in", routing.ids)],
            "res_model": "stock.source.relocate",
            "type": "ir.actions.act_window",
            "view_id": False,
            "view_mode": "tree,form",
            "limit": 20,
            "context": context,
        }
