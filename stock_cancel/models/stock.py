# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#    Ported to new API by Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, _, exceptions


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def has_valuation_moves(self):
        self.ensure_one()
        account_moves = self.env['account.move'].search(
            [('ref', '=', self.name)])
        return bool(account_moves)

    @api.multi
    def action_revert_done(self):
        quant_obj = self.env['stock.quant']
        for picking in self:
            if picking.has_valuation_moves():
                raise exceptions.Warning(
                    _('Picking %s has valuation moves: '
                        'remove them first.')
                    % (picking.name))
            if picking.invoice_id:
                raise exceptions.Warning(
                    _('Picking %s has invoices!') % (picking.name))
            for move in picking.move_lines:
                for quant in move.quant_ids:
                    if quant.location_id == move.location_dest_id:
                        if quant.qty != move.product_uom_qty:
                            raise exceptions.Warning(
                                _('Picking %s cannot be cancelled because '
                                  'their quants have later moves associated '
                                  'to them.')
                                % (picking.name))
                        quant_obj.quants_move(
                            [(quant, quant.qty)], move, move.location_id,
                            location_from=move.location_dest_id,
                            lot_id=quant.lot_id.id, owner_id=quant.owner_id.id)
                quant_obj.quants_unreserve(move)
            picking.move_lines.write({'state': 'draft'})
            picking.state = 'draft'
            if picking.invoice_state == 'invoiced' and not picking.invoice_id:
                picking.invoice_state = '2binvoiced'
            # Deleting the existing instance of workflow
            picking.delete_workflow()
            picking.create_workflow()
            picking.message_post(
                _("The picking has been re-opened and set to draft state"))
        return
