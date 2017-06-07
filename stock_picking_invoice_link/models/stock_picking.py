# -*- coding: utf-8 -*-
# © 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2015-2016 AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
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
    invoice_exists = fields.Boolean(
        u"Invoiced", compute='_compute_invoice_exists')

    @api.multi
    @api.depends('invoice_ids')
    def _compute_invoice_id(self):
        for picking in self:
            picking.invoice_id = picking.invoice_ids[:1]

    @api.multi
    @api.depends('invoice_ids')
    def _compute_invoice_exists(self):
        for picking in self:
            picking.invoice_exists = bool(picking.invoice_ids)

    @api.multi
    def action_view_invoice(self):
        """This function returns an action that display existing invoices
        of given stock pickings.
        It can either be a in a list or in a form view, if there is only
        one invoice to show.
        """
        self.ensure_one()
        action = self.env.ref('account.action_invoice_tree1')
        result = action.read()[0]
        if len(self.invoice_ids) > 1:
            result['domain'] = "[('id', 'in', %s)]" % self.invoice_ids.ids
        else:
            form_view = self.env.ref('account.invoice_form')
            result['views'] = [(form_view.id, 'form')]
            result['res_id'] = self.invoice_ids.id
        return result
