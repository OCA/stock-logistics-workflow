# -*- coding: utf-8 -*-
# Copyright 2016 Andrea Cometa - Apulia Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from openerp import models, fields, api
from openerp.addons.decimal_precision import decimal_precision as dp


class StockPickingPackagePreparation(models.Model):
    _inherit = 'stock.picking.package.preparation'

    @api.one
    def _compute_amount(self):
        self.amount_untaxed = 0.0
        self.amount_tax = 0.0
        self.amount_total = 0.0
        for picking in self.picking_ids:
            self.amount_untaxed += picking.amount_untaxed
            self.amount_tax += picking.amount_tax
            self.amount_total += picking.amount_total

    amount_untaxed = fields.Float(
        compute='_compute_amount', digits_compute=dp.get_precision('Account'),
        string='Untaxed Amount')
    amount_tax = fields.Float(
        compute='_compute_amount', digits_compute=dp.get_precision('Account'),
        string='Taxes')
    amount_total = fields.Float(
        compute='_compute_amount', digits_compute=dp.get_precision('Account'),
        string='Total')
