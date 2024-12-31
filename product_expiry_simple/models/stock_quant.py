# Copyright 2017-2022 Akretion France (http://www.akretion.com/)
# Copyright 2018-2022 Jarsa Sistemas (Alan Ramos <alan.ramos@jarsa.com.mx>)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    use_expiry_date = fields.Boolean(related="product_id.use_expiry_date", store=True)
    expiry_date = fields.Date(related="lot_id.expiry_date", store=True)
    expired = fields.Boolean(compute="_compute_expired", search="_search_expired")

    @api.depends("lot_id.expiry_date")
    def _compute_expired(self):
        for quant in self:
            quant.expired = quant.lot_id and quant.lot_id.expired or False

    def _search_expired(self, operator, value):
        quant_ids = []
        if operator == "=":
            today = fields.Date.context_today(self)
            domain = [("use_expiry_date", "=", True)]
            if value:
                domain.append(("expiry_date", "<", today))
            else:
                domain.append(("expiry_date", ">=", today))
            quant_ids = list(self._search(domain))
        res = [("id", "in", quant_ids)]
        return res

    def _get_gs1_barcode(self, gs1_quantity_rules_ai_by_uom):
        barcode = super()._get_gs1_barcode(gs1_quantity_rules_ai_by_uom)
        if self.product_id.use_expiry_date and self.expiry_date:
            barcode = f"17{self.expiry_date.strftime('%y%m%d')}{barcode}"
        return barcode

    # method copy/pasted from the official product_expiry module
    # Copyright Odoo SA
    @api.model
    def _get_removal_strategy_order(self, removal_strategy):
        if removal_strategy == "fefo":
            return "expiry_date, in_date, id"
        return super()._get_removal_strategy_order(removal_strategy)
