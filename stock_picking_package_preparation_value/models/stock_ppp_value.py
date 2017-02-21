# -*- coding: utf-8 -*-
# Copyright 2016 Andrea Cometa - Apulia Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from openerp import models, fields, api
from openerp.addons.decimal_precision import decimal_precision as dp


class StockPickingPackagePreparation(models.Model):
    _inherit = 'stock.picking.package.preparation'

    @api.multi
    def _compute_amount(self):
        for pack in self:
            pack.amount_untaxed = 0.0
            pack.amount_tax = 0.0
            pack.amount_total = 0.0
            for pack_line in pack.line_ids:
                if pack_line.move_id.procurement_id and\
                        pack_line.move_id.procurement_id.sale_line_id:
                    pack.amount_untaxed += pack_line.move_id.procurement_id.\
                        sale_line_id.price_subtotal
                    pack.amount_tax += pack_line.move_id.sale_taxes
            pack.amount_total += pack.amount_untaxed + pack.amount_tax

    amount_untaxed = fields.Float(
        compute='_compute_amount', digits_compute=dp.get_precision('Account'),
        string='Sale Untaxed Amount')
    amount_tax = fields.Float(
        compute='_compute_amount', digits_compute=dp.get_precision('Account'),
        string='Sale Taxes')
    amount_total = fields.Float(
        compute='_compute_amount', digits_compute=dp.get_precision('Account'),
        string='Sale Total')
