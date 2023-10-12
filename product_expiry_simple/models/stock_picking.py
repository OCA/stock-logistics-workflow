# Copyright 2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    show_expiry_warning = fields.Boolean(compute="_compute_show_expiry_warning")

    @api.depends(
        "state",
        "move_line_ids_without_package.lot_id.expiry_date",
        "move_line_ids_without_package.expiry_date",
    )
    def _compute_show_expiry_warning(self):
        today = fields.Date.context_today(self)
        for picking in self:
            show = False
            if picking.state in ("confirmed", "assigned"):
                for mline in picking.move_line_ids_without_package:
                    if mline.lot_id:
                        if (
                            mline.lot_id.expiry_date
                            and mline.lot_id.expiry_date < today
                        ):
                            show = True
                            break
                    elif mline.lot_name:
                        if mline.expiry_date and mline.expiry_date < today:
                            show = True
                            break
            picking.show_expiry_warning = show
