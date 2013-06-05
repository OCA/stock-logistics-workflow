# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
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

		
	def action_revert_done(self, cr, uid, ids, *args):
		if not len(ids):
			return False
		cr.execute('select id from stock_move where picking_id IN %s and state=%s', (tuple(ids), 'done'))
		line_ids = map(lambda x: x[0], cr.fetchall())
		self.write(cr, uid, ids, {'state': 'draft'})
		self.pool.get('stock.move').write(cr, uid, line_ids, { 'state': 'draft'})
		wf_service = netsvc.LocalService("workflow")
		for inv_id in ids:
			# Deleting the existing instance of workflow for SO
			wf_service.trg_delete(uid, 'stock.picking', inv_id, cr)
			wf_service.trg_create(uid, 'stock.picking', inv_id, cr)
		for (id,name) in self.name_get(cr, uid, ids):
			message = _("The stock picking '%s' has been set in draft state.") %(name,)
			self.log(cr, uid, id, message)
		return True

stock_picking()
