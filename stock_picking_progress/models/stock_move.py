# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    progress = fields.Float(
        compute="_compute_progress", store=True, group_operator="avg"
    )

    @api.depends(
        "product_uom_qty",
        "product_uom",
        "product_uom.rounding",
        "quantity_done",
        "state",
    )
    def _compute_progress(self):
        for record in self:
            if record.state == "done":
                record.progress = 100
                continue
            rounding = record.product_uom.rounding
            if float_is_zero(record.product_uom_qty, precision_rounding=rounding):
                record.progress = 0
            else:
                record.progress = (record.quantity_done / record.product_uom_qty) * 100
