# -*- coding: utf-8 -*-
# Copyright 2015-2016 Agile Business Group (<http://www.agilebg.com>)
# Copyright 2015 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def create(self, vals):
        period_obj = self.env['account.period']
        if self._context.get('move_date'):
            period_ids = period_obj.find(
                dt=self._context['move_date'])
            if period_ids:
                vals['period_id'] = period_ids[0].id
                vals['date'] = self._context['move_date']
        return super(AccountMove, self).create(vals)
