# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round

class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id):
        """
        Add an account move line with the valuation difference when returning goods.
        This feature is already existing in Odoo core but only for anglo-saxon accounting.
        """
        res = super(StockMove, self)._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id)
        #check if conditions are meet
        if self.product_id.cost_method == 'average' and not self.company_id.anglo_saxon_accounting:
            valuation_amount = cost if self.location_id.usage == 'supplier' and self.location_dest_id.usage == 'internal' else self.product_id.standard_price
            # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
            # the company currency... so we need to use round() before creating the accounting entries.
            debit_value = self.company_id.currency_id.round(valuation_amount * qty)
            credit_value = debit_value
            # in case of a supplier return, for products in average costing method, the stock_input
            # account books the real purchase price, while the stock account books the average price. The difference is
            # booked in the dedicated price difference account.
            if self.location_dest_id.usage == 'supplier' and self.origin_returned_move_id and self.origin_returned_move_id.purchase_line_id:
                debit_value = self.company_id.currency_id.round(self.origin_returned_move_id.price_unit * qty)
            # Opposite to Odoo Core concept, our findings are that in the same way a purchase return is made at the current product cost,
            # also in sale returns we should use the current product cost.
            if self.location_id.usage == 'customer' and self.origin_returned_move_id:
                #debit_value = self.origin_returned_move_id.price_unit * qty -- Odoo core error commented
                credit_value = self.company_id.currency_id.round(self.origin_returned_move_id.price_unit * qty)
            #if credit_value distinct than debit_value:
            if float_compare(credit_value, debit_value, precision_digits=self.company_id.currency_id.decimal_places) != 0:
                #change the amount of original line to keep the journal entry balanced
                for line in res:
                    if line[2]['credit']> 0.0:
                        line[2]['credit'] = credit_value
                    elif line[2]['debit'] > 0.0:
                        line[2]['debit'] = debit_value
                #continue computing the difference line
                partner_id = (self.picking_id.partner_id and self.env['res.partner']._find_accounting_partner(self.picking_id.partner_id).id) or False
                # for supplier returns of product in average costing method, in anglo saxon mode
                diff_amount = debit_value - credit_value
                price_diff_account = self.product_id.property_account_creditor_price_difference
                if not price_diff_account:
                    price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
                if not price_diff_account:
                    raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))
                price_diff_line = {
                    'name': self.name,
                    'product_id': self.product_id.id,
                    'quantity': qty,
                    'product_uom_id': self.product_id.uom_id.id,
                    'ref': self.picking_id.name,
                    'partner_id': partner_id,
                    'credit': diff_amount > 0 and diff_amount or 0,
                    'debit': diff_amount < 0 and -diff_amount or 0,
                    'account_id': price_diff_account.id,
                }
                res.append((0, 0, price_diff_line))
        return res
    