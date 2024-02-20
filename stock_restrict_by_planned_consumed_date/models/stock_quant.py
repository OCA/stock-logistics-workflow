# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _gather(self, *args, **kwargs):
        quants = super()._gather(*args, **kwargs)
        planned_consumed_date = self.env.context.get("restrict_planned_consumed_date")
        if planned_consumed_date:
            quants = quants.filtered(
                lambda quant, planned=planned_consumed_date: not quant.lot_id.expiration_date
                or quant.lot_id.expiration_date >= planned
            )
        return quants
