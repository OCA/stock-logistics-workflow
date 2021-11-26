# Copyright 2017-2021 Akretion France (http://www.akretion.com/)
# Copyright 2018-2021 Jarsa Sistemas (Alan Ramos <alan.ramos@jarsa.com.mx>)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    expiry_date = fields.Date(related="lot_id.expiry_date", store=True)
    expired = fields.Boolean(related="lot_id.expired")

    # method copy/pasted from the official product_expiry module
    # Copyright Odoo SA
    @api.model
    def _get_removal_strategy_order(self, removal_strategy):
        if removal_strategy == "fefo":
            return "expiry_date, in_date, id"
        return super()._get_removal_strategy_order(removal_strategy)
