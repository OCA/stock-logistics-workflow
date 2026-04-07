# Copyright 2024 ACSONE SA/NV
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _create_return(self):
        return_picking = super()._create_return()
        if self.picking_id.picking_type_id.empty_package_at_return:
            return_picking.move_line_ids.result_package_id = False
        return return_picking
