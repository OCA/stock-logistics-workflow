# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    expiry_date = fields.Date(
        related='lot_id.expiry_date', store=True, readonly=True)

    # method copy/pasted from the official product_expiry module
    # © Odoo SA
    @api.model
    def apply_removal_strategy(
            self, location, product, qty, domain, removal_strategy):
        if removal_strategy == 'fefo':
            order = 'expiry_date, location_id, package_id, lot_id, in_date, id'
            return self._quants_get_order(
                location, product, qty, domain, order)
        return super(StockQuant, self).apply_removal_strategy(
            location, product, qty, domain, removal_strategy)
