# -*- coding: utf-8 -*-
#
#
#    Author: Nicolas Bessi, Guewen Baconnier, Yannick Vaucher
#    Copyright 2013-2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
"""Adds a split button on stock picking out to enable partial picking without
   passing backorder state to done"""
from openerp import models, api, _


class stock_picking(models.Model):
    """Adds picking split without done state."""

    _inherit = "stock.picking"

    @api.multi
    def split_process(self):
        """Use to trigger the wizard from button with
           correct context"""
        ctx = {
            'active_model': self._name,
            'active_ids': self.ids,
            'active_id': len(self.ids) and self.ids[0] or False,
            'do_only_split': True,
            'default_picking_id': len(self.ids) and self.ids[0] or False,
        }

        view = self.env.ref('stock.view_stock_enter_transfer_details')
        return {
            'name': _('Enter quantities to split'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.transfer_details',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': ctx,
        }


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.model
    def split(self, move, qty,
              restrict_lot_id=False, restrict_partner_id=False):
        new_move_id = super(StockMove, self).split(
            move, qty,
            restrict_lot_id=restrict_lot_id,
            restrict_partner_id=restrict_partner_id,
        )
        new_move = self.browse(new_move_id)
        move_assigned = move.state == 'assigned'
        moves = move + new_move
        if move.reserved_availability > move.product_qty:
            moves.do_unreserve()
        if move.picking_id:
            move.picking_id.pack_operation_ids.unlink()
        if move_assigned:
            moves.action_assign()
        else:
            moves.action_confirm()
        if move.procurement_id:
            defaults = {'product_qty': qty,
                        'state': 'running'}
            new_procurement = move.procurement_id.copy(default=defaults)
            new_move.procurement_id = new_procurement
            move.procurement_id.product_qty = move.product_qty
        return new_move.id
