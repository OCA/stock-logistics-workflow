# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    deposit_location = fields.Boolean(
        string='Is a Deposit Location?',
        help='Check this box to allow using this location to put deposit '
             'goods.',
    )
