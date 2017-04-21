# -*- coding: utf-8 -*-
# Copyright 2017 Ursa Information Systems <http://www.ursainfosystems.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_hold = fields.Boolean(string='Sales Hold',
                               default=True,
                               help="If checked, all shipments for this "
                                      "customer will require approval from "
                                      "the Sales team.")
    credit_limit = fields.Monetary(string='Credit Limit')
    grace_period = fields.Integer(string='Grace Period',
                                  help="Grace period added on top of the "
                                       "customer payment term (in days)")
    credit_hold = fields.Boolean(string='Credit Hold',
                                 help="Place the customer on credit hold to "
                                      "prevent from shipping delivery "
                                      "orders")
