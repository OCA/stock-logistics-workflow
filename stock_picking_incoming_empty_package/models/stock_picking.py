# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        for picking in self:
            if (
                picking.picking_type_id.code == "incoming"
                and picking.picking_type_id.empty_package_at_validation
            ):
                picking.move_line_ids.filtered(
                    lambda ml: ml.result_package_id
                    and ml.result_package_id == ml.package_id
                ).result_package_id = False
        return super()._action_done()
