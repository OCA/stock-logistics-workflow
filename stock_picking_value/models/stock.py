# -*- coding: utf-8 -*-
# Copyright 2016 Andrea Cometa - Apulia Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from openerp import models, fields, api
from openerp.addons.decimal_precision import decimal_precision as dp


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    @api.depends('sale_id.amount_untaxed', 'sale_id.amount_tax',
                 'sale_id.amount_total')
    def _compute_amount(self):
        self.ensure_one()
        if self.sale_id:
            if self.pack_operation_ids:
                for operation in self.pack_operation_ids:
                    self.amount_untaxed += operation.sale_subtotal
                    self.amount_tax += operation.sale_taxes
                self.amount_total = self.amount_untaxed + self.amount_tax
            else:
                for move in self.move_lines:
                    self.amount_untaxed += move.sale_subtotal
                    self.amount_tax += move.sale_taxes
                self.amount_total = self.amount_untaxed + self.amount_tax

    amount_untaxed = fields.Float(
        compute='_compute_amount',
        digits_compute=dp.get_precision('Account'),
        string='Untaxed Amount')
    amount_tax = fields.Float(
        compute='_compute_amount',
        digits_compute=dp.get_precision('Account'),
        string='Taxes')
    amount_total = fields.Float(
        compute='_compute_amount',
        digits_compute=dp.get_precision('Account'),
        string='Total')
    stock_valued = fields.Boolean(string="Stock Valued")


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    @api.depends('procurement_id.sale_line_id',
                 'procurement_id.sale_line_id.price_unit',
                 'procurement_id.sale_line_id.discount',
                 'procurement_id.sale_line_id.price_subtotal',
                 'procurement_id.sale_line_id.price_reduce',
                 'procurement_id.sale_line_id.order_id')
    def _compute_sale_prices(self):
        for move in self:
            if move.procurement_id.sale_line_id:
                sale_line = move.procurement_id.sale_line_id
                move.sale_taxes = sale_line.product_uom_qty and round(
                    ((sale_line.order_id._amount_line_tax(sale_line) /
                      sale_line.product_uom_qty) * move.product_qty),
                    dp.get_precision('Account')(move._cr)[1]) or 0.00
                move.sale_price_untaxed = sale_line.price_reduce
                move.sale_price_unit = sale_line.price_unit
                move.sale_discount = sale_line.discount
                move.sale_subtotal = round(
                    sale_line.price_reduce * move.product_qty,
                    dp.get_precision('Account')(move._cr)[1])
            else:
                move.sale_taxes = 0
                move.sale_price_untaxed = 0
                move.sale_subtotal = 0
                move.sale_price_unit = 0
                move.sale_discount = 0

    sale_subtotal = fields.Float(
        compute='_compute_sale_prices',
        digits_compute=dp.get_precision('Account'),
        string='Subtotal')
    sale_price_unit = fields.Float(
        compute='_compute_sale_prices',
        digits_compute=dp.get_precision('Account'),
        string='Price')
    sale_price_untaxed = fields.Float(
        compute='_compute_sale_prices',
        digits_compute=dp.get_precision('Account'),
        string='Price Untaxed')
    sale_taxes = fields.Float(
        compute='_compute_sale_prices',
        digits_compute=dp.get_precision('Account'),
        string='Total Taxes')
    sale_discount = fields.Float(
        compute='_compute_sale_prices',
        digits_compute=dp.get_precision('Account'),
        string='Discount (%)')


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    @api.multi
    def _compute_sale_prices(self):
        self.ensure_one()
        self.sale_taxes = 0
        self.sale_price_untaxed = 0
        self.sale_subtotal = 0
        self.sale_price_unit = 0
        self.sale_discount = 0
        if self.linked_move_operation_ids:
            move = self.linked_move_operation_ids[0].move_id
            if move.procurement_id.sale_line_id:
                self.sale_taxes = round(
                    (move.sale_taxes / move.product_qty) * self.product_qty,
                    dp.get_precision('Account')(self._cr)[1])
                self.sale_price_untaxed = move.sale_price_untaxed
                self.sale_price_unit = move.sale_price_unit
                self.sale_discount = move.sale_discount
                self.sale_subtotal = round(
                    self.sale_price_untaxed * self.product_qty,
                    dp.get_precision('Account')(self._cr)[1])

    sale_subtotal = fields.Float(
        compute='_compute_sale_prices',
        digits_compute=dp.get_precision('Account'),
        string='Subtotal')
    sale_price_unit = fields.Float(
        compute='_compute_sale_prices',
        digits_compute=dp.get_precision('Account'),
        string='Price')
    sale_price_untaxed = fields.Float(
        compute='_compute_sale_prices',
        digits_compute=dp.get_precision('Account'),
        string='Price Untaxed')
    sale_taxes = fields.Float(
        compute='_compute_sale_prices',
        digits_compute=dp.get_precision('Account'),
        string='Total Taxes')
    sale_discount = fields.Float(
        compute='_compute_sale_prices',
        digits_compute=dp.get_precision('Account'),
        string='Discount (%)')
