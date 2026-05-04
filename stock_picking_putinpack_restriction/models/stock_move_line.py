# Copyright 2023 Camptocamp (https://www.camptocamp.com)
# Copyright 2024 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _action_done(self):
        res = super()._action_done()

        # We must filter by .exists() because super() may unlink some move lines
        existing_lines = self.exists()
        restricted_lines = existing_lines.filtered(
            lambda line: line.move_id.picking_type_id.put_in_pack_restriction
        )

        for line in restricted_lines:
            picking_type = line.move_id.picking_type_id
            restriction = picking_type.put_in_pack_restriction
            has_package = bool(line.result_package_id)

            if restriction == "no_package" and has_package:
                raise ValidationError(
                    _(
                        "Using a package on transfer type %(name)s is not allowed.",
                        name=picking_type.display_name,
                    )
                )

            if restriction == "with_package" and not has_package:
                raise ValidationError(
                    _(
                        "A package is required for transfer type %(name)s.",
                        name=picking_type.display_name,
                    )
                )

        return res
