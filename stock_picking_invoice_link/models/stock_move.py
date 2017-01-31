# -*- coding: utf-8 -*-
# © 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    invoice_line_id = fields.Many2one(comodel_name='account.invoice.line',
                                      string='Invoice Line', readonly=True)
