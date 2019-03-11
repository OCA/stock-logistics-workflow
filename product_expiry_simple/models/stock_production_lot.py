# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    expiry_date = fields.Date(string='Expiry Date')

    @api.depends('name', 'expiry_date')
    def name_get(self):
        res = []
        for lot in self:
            dname = lot.name
            if lot.expiry_date:
                dname = '[%s] %s' % (lot.expiry_date, dname)
            res.append((lot.id, dname))
        return res
