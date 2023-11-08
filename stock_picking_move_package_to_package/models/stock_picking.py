# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _move_package_to_package(self):
        for picking in self:
            if picking.picking_type_entire_packs:
                for package_level in picking.package_level_ids.filtered(
                    "package_dest_id"
                ):
                    # Get the quants from the source package
                    quants_to_move = package_level.package_id.quant_ids
                    # Update the package_id of quants to the destination package
                    quants_to_move.write(
                        {"package_id": package_level.package_dest_id.id}
                    )

    def button_validate(self):
        res = super().button_validate()
        if res is not True:
            return res
        self._move_package_to_package()
        return res
