# -*- coding: utf-8 -*-
# Copyright 2017 Ursa Information Systems <http://www.ursainfosystems.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sales_hold = fields.Boolean(string="Sales Hold")
    credit_hold = fields.Boolean(related='partner_id.credit_hold',
                                 string="Credit Hold",
                                 readonly=True,
                                 required=True)
    credit_override = fields.Boolean(string="Override Credit Hold",
                                     track_visibility='onchange',
                                     default=False)

    @api.onchange('partner_id')
    def onchange_partner_hold_details(self):
        if self.partner_id:
            # If partner has a credit hold
            if self.partner_id.credit_hold:
                self.partner_id = False
                # Display that the customer is on credit hold
                warning = {
                    'title': _('Validation Error!'),
                    'message': _('The customer is on credit hold!'),
                }
                return {'warning': warning}
            else:
                self.sales_hold = self.partner_id.sale_hold

    @api.multi
    def action_confirm(self):
        if self.partner_id.credit_hold:
            message = _('The customer is on credit hold.')
            # Display that the customer is on credit hold
            raise ValidationError(message)
        else:
            return super(SaleOrder, self).action_confirm()
