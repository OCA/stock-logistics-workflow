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
                product_names = ", ".join(
                    lines_missing_lotinfo.mapped("product_id.display_name")
                )
                raise exceptions.UserError(
                    _(
                        "Missing Lot Info for Products: %(product_names)s.",
                        product_names=product_names,
                    )
                )

    def button_validate(self):
        res = super().button_validate()
        self._check_required_lot_info()
        return res
