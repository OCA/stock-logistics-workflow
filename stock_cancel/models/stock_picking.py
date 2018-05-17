# -*- coding: utf-8 -*-
# Copyright 2012 Andrea Cometa
# Copyright 2013 Agile Business Group sagl
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models, exceptions, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def cancel_valuation_moves(self):
        self.ensure_one()
        account_moves = self.env['account.move'].search(
            [('ref', '=', self.name)])
        account_moves.button_cancel()
        return account_moves

    def _check_restrictions(self):
        # returned_move_ids in stock.move
        # split_from in stock.move
        if self.search([('backorder_id', '=', self.id)], limit=1):
            raise exceptions.UserError(
                _('Not Allowed, picking has backorder.'))  # noqa

    @api.multi
    def action_revert_done(self):
        for picking in self:
            picking._check_restrictions()
            acc_moves = picking.cancel_valuation_moves()
            acc_moves.unlink()
            if picking.invoice_id.filtered(
                    lambda order: order.state != 'cancel'):
                raise exceptions.UserError(
                    _('Picking %s has invoices') % (picking.name))
            picking.move_lines.write({'state': 'draft'})
            # reassign quants done
            for move in picking.move_lines:
                move._check_restrictions()
                move.quant_ids._revert()

            picking.group_id.procurement_ids.reset_to_confirmed()
            sale_lines = picking.group_id.procurement_ids.mapped(
                'sale_line_id')
            for line in sale_lines:
                line.qty_delivered = line._get_delivered_qty()
            picking.state = 'draft'
            picking.action_confirm()
            picking.do_prepare_partial()
            picking.message_post(
                _("The picking has been re-opened and set to draft state"))
        return
