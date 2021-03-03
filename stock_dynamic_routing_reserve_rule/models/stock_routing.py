# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from os.path import commonpath

from odoo import _, api, fields, models


class StockRouting(models.Model):
    _inherit = "stock.routing"

    reserve_rule_warning = fields.Html(compute="_compute_reserve_rule_warning")

    def _removal_rules_common_locations(self, reserve_rules):
        dest_removal_locations = reserve_rules.rule_removal_ids.location_id
        location_names = dest_removal_locations.mapped("complete_name")
        locations_common_path = commonpath(location_names)
        location_names = [
            name[len(locations_common_path) :].lstrip("/") for name in location_names
        ]
        return locations_common_path, location_names

    def _render_reserve_rule_warning(self):
        messages = []
        src_picking_type = self.picking_type_id
        src_reserve_rule = src_picking_type.reserve_rule_ids
        for routing_rule in self.rule_ids:
            dest_picking_type = routing_rule.picking_type_id

            if src_reserve_rule and not dest_picking_type.reserve_rule_ids:
                (
                    location_common_path,
                    location_names,
                ) = self._removal_rules_common_locations(src_reserve_rule)
                messages.append(
                    self.env["ir.qweb"].render(
                        "stock_dynamic_routing_reserve_rule."
                        "routing_rule_reserve_rule_warning_src",
                        values={
                            "src_picking_type": src_picking_type,
                            "location_common_path": location_common_path,
                            "location_names": ", ".join(location_names),
                            "dest_picking_type": dest_picking_type,
                        },
                    )
                )
            elif dest_picking_type.reserve_rule_ids and not src_reserve_rule:
                (
                    location_common_path,
                    location_names,
                ) = self._removal_rules_common_locations(
                    dest_picking_type.reserve_rule_ids
                )
                messages.append(
                    self.env["ir.qweb"].render(
                        "stock_dynamic_routing_reserve_rule."
                        "routing_rule_reserve_rule_warning_dest",
                        values={
                            "dest_picking_type": dest_picking_type,
                            "location_common_path": location_common_path,
                            "location_names": ", ".join(location_names),
                            "src_picking_type": src_picking_type,
                        },
                    )
                )
        return messages

    @api.depends(
        "picking_type_id.reserve_rule_ids.rule_removal_ids.location_id",
        "rule_ids.picking_type_id.reserve_rule_ids.rule_removal_ids.location_id",
    )
    def _compute_reserve_rule_warning(self):
        for routing in self:
            routing.reserve_rule_warning = b"".join(
                routing._render_reserve_rule_warning()
            )

    def action_view_reserve_rule(self):
        picking_types = self.picking_type_id | self.rule_ids.picking_type_id
        reserve_rules = self.env["stock.reserve.rule"].search(
            [("picking_type_ids", "in", picking_types.ids)]
        )
        context = self.env.context
        if len(picking_types) == 1:
            context = dict(context, default_picking_type_id=picking_types.id)
        return {
            "name": _("Reservation Rules"),
            "domain": [("id", "in", reserve_rules.ids)],
            "res_model": "stock.reserve.rule",
            "type": "ir.actions.act_window",
            "view_id": False,
            "view_mode": "tree,form",
            "context": context,
        }
