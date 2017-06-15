# -*- coding: utf-8 -*-
# © 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2015-2016 AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    invoice_ids = fields.Many2many(
        comodel_name='account.invoice', copy=False, string='Invoices',
        readonly=True)
    # Provide this field for backwards compatibility
    invoice_id = fields.Many2one(
        comodel_name='account.invoice', string='Invoice',
        compute="_compute_invoice_id")

    @api.multi
    @api.depends('invoice_ids')
    def _compute_invoice_id(self):
        for picking in self:
            picking.invoice_id = picking.invoice_ids[:1]
