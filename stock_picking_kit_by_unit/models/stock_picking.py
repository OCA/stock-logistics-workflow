# Copyright (C) 2023 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    kit_move_line_ids = fields.One2many(
        "stock.move.line",
        compute="_compute_kit_move_line_ids",
    )
    has_kit_lines = fields.Boolean(
        compute="_compute_kit_move_line_ids",
    )

    @api.depends("move_line_ids.kit_product_id")
    def _compute_kit_move_line_ids(self):
        for picking in self:
            kit_lines = picking.move_line_ids.filtered("kit_product_id")
            picking.kit_move_line_ids = kit_lines
            picking.has_kit_lines = bool(kit_lines)

    def action_kit_operations(self):
        """Open a filtered view of move lines belonging to kit explosions.

        Assigns kit_sequence before opening so the view sorts per-box.
        """
        self.ensure_one()
        self.kit_move_line_ids._assign_kit_sequence()
        view_id = self.env.ref(
            "stock_picking_kit_by_unit.view_stock_move_line_kit_operations_tree"
        ).id
        return {
            "name": self.env._("Kit Operations"),
            "view_mode": "list",
            "type": "ir.actions.act_window",
            "res_model": "stock.move.line",
            "views": [(view_id, "list")],
            "domain": [("id", "in", self.kit_move_line_ids.ids)],
            "context": {
                "default_picking_id": self.id,
                "default_location_id": self.location_id.id,
                "default_location_dest_id": self.location_dest_id.id,
                "default_company_id": self.company_id.id,
                "show_lots_text": self.show_lots_text,
                "picking_code": self.picking_type_code,
                "kit_picking_id": self.id,
            },
        }

    def action_pack_all_kits(self):
        """Group kit move lines per kit unit and create a package per group.

        Each package is named after the first serial number in the group.
        Only processes lines that are not already packed.
        """
        self.ensure_one()
        if not self.env.user.has_group("stock.group_tracking_lot"):
            return

        kit_lines = self.kit_move_line_ids.filtered(lambda ml: not ml.result_package_id)
        if not kit_lines:
            return

        for box_lines in kit_lines._get_kit_box_groups():
            # Skip box if any tracked line is missing a lot
            tracked = box_lines.filtered("lots_visible")
            if tracked and not all(ml.lot_name or ml.lot_id for ml in tracked):
                continue
            first_lot = box_lines.filtered("lot_name")[:1].lot_name
            box_lines._put_in_pack(package_name=first_lot or False)

    def button_validate(self):
        """Auto-pack kit lines before validation if not already packed."""
        for picking in self:
            unpacked_kit_lines = picking.kit_move_line_ids.filtered(
                lambda ml: not ml.result_package_id
            )
            if unpacked_kit_lines:
                picking.action_pack_all_kits()
        return super().button_validate()
