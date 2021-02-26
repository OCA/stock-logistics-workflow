# Copyright 2021 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, datetime
from dateutil.relativedelta import relativedelta 
from odoo import models, fields, api, _


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def _procurement_from_orderpoint_get_groups(self, orderpoint_ids):
        param_obj = self.env['ir.config_parameter']

        # get system parameter to check if limit virtual stock at date:
        # and set this param into context.
        purchase_limit_days = param_obj.sudo().get_param(
            'stock_picking_purchase_limit_date.purchase_limit_days')

        limit_date = False
        if purchase_limit_days:
            limit_date = date.today() + relativedelta(days=int(purchase_limit_days))
        return [{
            'to_date': limit_date,
            'procurement_values': dict()
        }]
