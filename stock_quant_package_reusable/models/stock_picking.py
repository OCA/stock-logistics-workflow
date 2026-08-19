# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_put_in_pack(self, move_lines_to_pack=False):
        self.ensure_one()
        # reusable_package_id is set in context by select.reusable.package wizard
        if self.picking_type_id.use_reusable_pack and not self.env.context.get(
            "reusable_package_id"
        ):
            return {
                "name": _("Select Reusable Package"),
                "type": "ir.actions.act_window",
                "res_model": "select.reusable.package",
                "view_mode": "form",
                "target": "new",
                "context": {
                    "default_picking_id": self.id,
                    "move_lines_to_pack": move_lines_to_pack,
                },
            }
        return super().action_put_in_pack(move_lines_to_pack=move_lines_to_pack)

    def _put_in_pack(self, move_line_ids):
        # reusable_package_id is set in context by select.reusable.package wizard
        if not (reusable_package_id := self.env.context.get("reusable_package_id")):
            return super()._put_in_pack(move_line_ids)
        package = self.env["stock.quant.package"].browse(reusable_package_id)

        # Same logic than stock.picking::_put_in_pack from stock module
        package_type = move_line_ids.move_id.product_packaging_id.package_type_id
        if len(package_type) == 1:
            package.package_type_id = package_type
        if len(move_line_ids) == 1:
            default_dest_location = move_line_ids._get_default_dest_location()
            move_line_ids.location_dest_id = (
                default_dest_location._get_putaway_strategy(
                    product=move_line_ids.product_id,
                    quantity=move_line_ids.quantity,
                    package=package,
                )
            )
        move_line_ids.write({"result_package_id": package.id})
        if len(self) == 1:
            self.env["stock.package_level"].with_context(from_put_in_pack=True).create(
                {
                    "package_id": package.id,
                    "picking_id": self.id,
                    "location_id": False,
                    "location_dest_id": move_line_ids.location_dest_id.id,
                    "move_line_ids": [(6, 0, move_line_ids.ids)],
                    "company_id": self.company_id.id,
                }
            )
        return package
