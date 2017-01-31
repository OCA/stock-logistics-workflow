# -*- coding: utf-8 -*-
# © 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    invoice_id = fields.Many2one(comodel_name='account.invoice',
                                 string='Invoice', readonly=True)
