# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
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

from openerp.osv import orm
from openerp.tools.translate import _
import netsvc


class stock_move(orm.Model):
    _inherit = 'stock.move'

    def action_revert_done(self, cr, uid, ids, context=None):
        picking_obj = self.pool['stock.picking']
        for move in self.browse(cr, uid, ids, context):
            if picking_obj.has_valuation_moves(cr, uid, move):
                raise orm.except_orm(
                    _('Error'),
                    _('Line %s has valuation moves. \
                        Remove them first') % (move.name))
            move.write({'state': 'draft'})
            if move.picking_id:
                picking_obj._reopen_picking(
                    cr, uid, move.picking_id, context=context)

        for (id, name) in self.name_get(cr, uid, ids):
            message = _(
                "The stock move '%s' has been set in draft state."
            ) % (name,)
            self.log(cr, uid, id, message)
        return True


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def has_valuation_moves(self, cr, uid, move):
        return self.pool.get('account.move').search(cr, uid, [
            ('ref', '=', move.picking_id.name),
        ])

    def _reopen_picking(self, cr, uid, picking, context=None):
        self.write(cr, uid, [picking.id], {'state': 'draft'})
        if picking.invoice_state == 'invoiced' and not picking.invoice_id:
            self.write(cr, uid, [picking.id],
                       {'invoice_state': '2binvoiced'})
        wf_service = netsvc.LocalService("workflow")
        # Deleting the existing instance of workflow
        wf_service.trg_delete(uid, 'stock.picking', picking.id, cr)
        wf_service.trg_create(uid, 'stock.picking', picking.id, cr)
        return True

    def action_revert_done(self, cr, uid, ids, context=None):
        if not len(ids):
            return False
        for picking in self.browse(cr, uid, ids, context):
            for line in picking.move_lines:
                if self.has_valuation_moves(cr, uid, line):
                    raise orm.except_orm(
                        _('Error'),
                        _('Line %s has valuation moves (%s). \
                            Remove them first') % (line.name,
                                                   line.picking_id.name))
                line.write({'state': 'draft'})
            self._reopen_picking(cr, uid, picking, context=context)

        for (id, name) in self.name_get(cr, uid, ids):
            message = _(
                "The stock picking '%s' has been set in draft state."
            ) % (name,)
            self.log(cr, uid, id, message)
        return True


class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'

    def action_revert_done(self, cr, uid, ids, context=None):
        # override in order to redirect to stock.picking object
        return self.pool.get('stock.picking').action_revert_done(
            cr, uid, ids, context=context)


class stock_picking_in(orm.Model):
    _inherit = 'stock.picking.in'

    def action_revert_done(self, cr, uid, ids, context=None):
        # override in order to redirect to stock.picking object
        return self.pool.get('stock.picking').action_revert_done(
            cr, uid, ids, context=context)
