# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierre@verkest.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _gather(self, *args, **kwargs):
        quants = super()._gather(*args, **kwargs)
        restrict_expiration_date = self.env.context.get("restrict_expiration_date")
        if restrict_expiration_date:
            quants = quants.filtered(
                lambda quant, restrict_expiration_date=restrict_expiration_date: quant.lot_id
                is False
                or quant.lot_id
                and quant.lot_id.expiration_date.date() == restrict_expiration_date
            )
        return quants
