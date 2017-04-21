# -*- coding: utf-8 -*-
# Copyright 2017 Ursa Information Systems <http://www.ursainfosystems.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def check_limit(self, sale_id):

        # Other orders for this partner
        order_ids = self.env['sale.order'].search([('partner_id', '=',
                                                    sale_id.partner_id.id),
                                                   ('state', 'in',
                                                    ['progress', 'manual',
                                                     'invoice_except'])])

        # Open invoices (unpaid or partially paid invoices)
        # it is already included in partner.credit
        invoice_ids = self.env['account.invoice'].\
            search([('partner_id', '=', sale_id.partner_invoice_id.id),
                    ('state', '=', 'open'),
                    ('type', 'in', ['out_invoice', 'out_refund'])])

        # Initialize variables
        existing_order_balance = 0.0
        existing_invoice_balance = 0.0

        # Confirmed orders - invoiced - draft or open / not invoiced
        for order in order_ids:
            existing_order_balance = existing_order_balance +\
                                     order.amount_total

        # Invoices that are open also shows up as part of partner.credit,
        # so must be deducted
        for invoice in invoice_ids:
            if (datetime.strptime(invoice.date_due, "%Y-%m-%d") +
                    timedelta(days=sale_id.partner_id.grace_period))\
                    < datetime.now():
                return True
            else:
                existing_invoice_balance += invoice.residual

        # All open sale orders + partner credit (AR balance) - open invoices
        # (already included in partner credit)
        if sale_id.partner_id.credit_limit and (existing_invoice_balance +
                                                existing_order_balance +
                                                sale_id.amount_total)\
                > sale_id.partner_id.credit_limit:
            return True
        else:
            return False

    @api.multi
    def _get_allow_transfer(self):
        result = False
        for record in self:
            # Only outgoing picking
            if record.picking_type_code == 'outgoing':
                # Sales person has a hold
                if record.sale_id.sales_hold:
                    result = True
                # Accounting has credit hold on partner
                elif record.sale_id.partner_id.credit_hold:
                    if not record.sale_id.credit_override:
                        result = True
                # Partner will exceed limit with current sale order or is
                # over-due
                elif record.check_limit(record.sale_id):
                    if not record.sale_id.credit_override:
                        result = True
                record.dont_allow_transfer = result

    dont_allow_transfer = fields.Boolean(string="Hold Transfer",
                                         compute='_get_allow_transfer')

    @api.multi
    def do_new_transfer(self):

        if self.dont_allow_transfer:
            raise UserError(_("Customer has a shipment hold.\n\n"
                              "Contact Sales/Accounting to verify sales "
                              "hold/credit hold/overdue payments."))

        # Only outgoing picking
        if self.picking_type_code == 'outgoing':
            message = ''
            # Sales order on hold
            if self.sale_id.sales_hold:

                # Customer is on sales hold
                message += _('{0} is on sales hold.\n'.format(
                    self.partner_id.name))

            else:
                if self.dont_allow_transfer:
                    # Customer is on credit hold / exceeded limit
                    message += _('{0} is on credit hold or over credit limit.\n'.format(self.partner_id.name))  # noqa

            if message:
                raise ValidationError(message)
            else:
                return super(StockPicking, self).do_new_transfer()

        # Incoming shipments / internal transfers
        else:
            return super(StockPicking, self).do_new_transfer()
