# Copyright 2019 Komit Consulting - Duc Dao Dong
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    currency_id = fields.Many2one(
        'res.currency', required=True,
        states={'done': [('readonly', True)]},
        default=lambda self: self.env.user.company_id.currency_id)

    @api.onchange('account_journal_id')
    def _onchange_account_journal_id(self):
        if self.account_journal_id and self.account_journal_id.currency_id:
            self.currency_id = self.account_journal_id.currency_id

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        if self.currency_id:
            self.cost_lines._onchange_currency_price_unit()
