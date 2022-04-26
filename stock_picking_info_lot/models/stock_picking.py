# Copyright 2022 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, exceptions, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _check_required_lot_info(self):
        for picking in self:
            lines_missing_lotinfo = picking.move_line_ids_without_package.filtered(
                lambda x: x.lot_info_usage == "required" and not x.lot_info
            )
            if lines_missing_lotinfo:
                raise exceptions.UserError(
                    _("Missing Lot Info for Products %s.")
                    % ", ".join(lines_missing_lotinfo.product_id.mapped("display_name"))
                )

    def button_validate(self):
        res = super().button_validate()
        self._check_required_lot_info()
        return res
