# Copyright 2023 Camptocamp (https://www.camptocamp.com)
# Copyright 2024 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_put_in_pack_picking_types(self):
        return self.move_id.picking_type_id | self.picking_type_id

    def action_put_in_pack(
        self,
        *,
        package_id=False,
        package_type_id=False,
        package_name=False,
        package_capacity=None,
    ):
        # Check here (and not in _pre_put_in_pack_hook) so that every way to
        # put in pack is covered, including the split by package capacity.
        move_lines = self
        if self.env.context.get("all_move_line_ids"):
            move_lines |= self.browse(self.env.context["all_move_line_ids"])
        move_lines._get_put_in_pack_picking_types()._check_put_in_pack_allowed()
        return super().action_put_in_pack(
            package_id=package_id,
            package_type_id=package_type_id,
            package_name=package_name,
            package_capacity=package_capacity,
        )

    def _action_done(self):
        res = super()._action_done()

        # We must filter by .exists() because super() may unlink some move lines
        existing_lines = self.exists()
        for line in existing_lines:
            picking_type = line.move_id.picking_type_id or line.picking_type_id
            restriction = picking_type.put_in_pack_restriction
            if not restriction:
                continue
            has_package = bool(line.result_package_id)

            if restriction == "no_package" and has_package:
                raise ValidationError(
                    self.env._(
                        "Using a package on transfer type %(name)s is not allowed.",
                        name=picking_type.display_name,
                    )
                )

            if restriction == "with_package" and not has_package:
                raise ValidationError(
                    self.env._(
                        "A package is required for transfer type %(name)s.",
                        name=picking_type.display_name,
                    )
                )

        return res
