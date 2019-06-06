# Copyright 2017-2019 Akretion France (http://www.akretion.com/)
# Copyright 2018 Jarsa Sistemas (Alan Ramos <alan.ramos@jarsa.com.mx>)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    expiry_date = fields.Date(string='Expiry Date')
    expired = fields.Boolean(compute='_compute_expired')

    def _compute_expired(self):
        today = fields.Date.context_today(self)
        for lot in self:
            expired = False
            if lot.expiry_date and lot.expiry_date < today:
                expired = True
            lot.expired = expired

    @api.depends('name', 'expiry_date')
    def name_get(self):
        res = []
        today = fields.Date.context_today(self)
        for lot in self:
            dname = lot.name
            if lot.expiry_date:
                if lot.expiry_date < today:
                    dname = _('[%s Expired] %s') % (lot.expiry_date, dname)
                else:
                    dname = '[%s] %s' % (lot.expiry_date, dname)
            res.append((lot.id, dname))
        return res
