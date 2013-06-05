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
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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
# W gli spaghetti code!!!
##############################################################################


from osv import osv, fields
import netsvc
from tools.translate import _

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    def has_valuation_moves(self, cr, uid, move):
        return self.pool.get('account.move').search(cr, uid, [
            ('ref','=', move.picking_id.name),
            ])

    def action_revert_done(self, cr, uid, ids, context=None):
        if not len(ids):
            return False
        for picking in self.browse(cr, uid, ids, context):
            for line in picking.move_lines:
                if self.has_valuation_moves(cr, uid, line):
                    raise osv.except_osv(_('Error'),
                        _('Line %s has valuation moves (%s). Remove them first')
                        % (line.name, line.picking_id.name))
                line.write({'state': 'draft'})
            self.write(cr, uid, [picking.id], {'state': 'draft'})
            if picking.invoice_state == 'invoiced' and not picking.invoice_id:
                self.write(cr, uid, [picking.id], {'invoice_state': '2binvoiced'})
            wf_service = netsvc.LocalService("workflow")
            # Deleting the existing instance of workflow
            wf_service.trg_delete(uid, 'stock.picking', picking.id, cr)
            wf_service.trg_create(uid, 'stock.picking', picking.id, cr)
        for (id,name) in self.name_get(cr, uid, ids):
            message = _("The stock picking '%s' has been set in draft state.") %(name,)
            self.log(cr, uid, id, message)
        return True

class stock_picking_out(osv.osv):
    _inherit = 'stock.picking.out'
    def action_revert_done(self, cr, uid, ids, context=None):
        #override in order to redirect to stock.picking object
        return self.pool.get('stock.picking').action_revert_done(cr, uid, ids, context=context)

class stock_picking_in(osv.osv):
    _inherit = 'stock.picking.in'
    def action_revert_done(self, cr, uid, ids, context=None):
        #override in order to redirect to stock.picking object
        return self.pool.get('stock.picking').action_revert_done(cr, uid, ids, context=context)
