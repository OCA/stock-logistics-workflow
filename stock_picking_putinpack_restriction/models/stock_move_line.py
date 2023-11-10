# Copyright 2023 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _action_done(self):
        for line in self:
            picking_type = line.move_id.picking_type_id
            restriction = picking_type.put_in_pack_restriction
            if not restriction:
                continue
            line_has_package = bool(line.result_package_id)
            if restriction == "no_package" and line_has_package:
                raise ValidationError(
                    _("Using a package on transfer type %s is not allowed.")
                    % picking_type.name
                )
            if restriction == "with_package" and not line_has_package:
                raise ValidationError(
                    _("A package is required for transfer type %s.") % picking_type.name
                )
        return super()._action_done()
