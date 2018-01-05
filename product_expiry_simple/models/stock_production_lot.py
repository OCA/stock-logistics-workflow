# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2018 Jarsa Sistemas (Alan Ramos <alan.ramos@jarsa.com.mx>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    expiry_date = fields.Date(string='Expiry Date')
    display_name = fields.Char(
        compute='_compute_display_name',
        string='Lot/Serial Number Display', store=True, readonly=True)

    @api.multi
    @api.depends('name', 'expiry_date')
    def _compute_display_name(self):
        for lot in self:
            dname = lot.name
            if lot.expiry_date:
                dname = '[%s] %s' % (lot.expiry_date, dname)
            lot.display_name = dname
