# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2018 Jarsa Sistemas (Alan Ramos <alan.ramos@jarsa.com.mx>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    expiry_date = fields.Date(
        related='lot_id.expiry_date', store=True, readonly=True)

    # method copy/pasted from the official product_expiry module
    # © Odoo SA
    @api.model
    def _get_removal_strategy_order(self, removal_strategy):
        if removal_strategy == 'fefo':
            return 'expiry_date, in_date, id'
        return super(StockQuant, self)._get_removal_strategy_order(
            removal_strategy)
