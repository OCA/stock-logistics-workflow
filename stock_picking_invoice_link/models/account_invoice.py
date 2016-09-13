# -*- coding: utf-8 -*-
# © 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2015-2016 AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    picking_ids = fields.Many2many(
        comodel_name='stock.picking', string='Related Pickings',
        compute="_compute_picking_ids")

    @api.multi
    def _compute_picking_ids(self):
        for invoice in self:
            invoice.picking_ids = self.env['stock.picking']
            for line in invoice.invoice_line_ids:
                invoice.picking_ids |= line.move_line_ids.mapped('picking_id')


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    move_line_ids = fields.Many2many(
        comodel_name='stock.move', string='Related Stock Moves',
        compute="_compute_move_line_ids")

    @api.multi
    def _compute_move_line_ids(self):
        for line in self:
            line.move_line_ids = self.env['stock.move']
            for sale_line in line.sale_line_ids:
                for proc in sale_line.procurement_ids:
                    line.move_line_ids |= proc.move_ids
