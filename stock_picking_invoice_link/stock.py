# -*- coding: utf-8 -*-
##############################################################################
#
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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class stock_move(orm.Model):
    _inherit = "stock.move"

    _columns = {
        'invoice_line_id': fields.many2one(
            'account.invoice.line', 'Invoice line', readonly=True),
    }


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    _columns = {
        'invoice_id': fields.many2one(
            'account.invoice', 'Invoice', readonly=True),
    }

    def _invoice_hook(self, cr, uid, picking, invoice_id):
        res = super(stock_picking, self)._invoice_hook(
            cr, uid, picking, invoice_id)
        picking.write({'invoice_id': invoice_id})
        return res

    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        res = super(stock_picking, self)._invoice_line_hook(
            cr, uid, move_line, invoice_line_id)
        move_line.write({'invoice_line_id': invoice_line_id})
        return res


class stock_picking_out(orm.Model):
    _inherit = "stock.picking.out"

    _columns = {
        'invoice_id': fields.many2one(
            'account.invoice', 'Invoice', readonly=True),
    }


class stock_picking_in(orm.Model):
    _inherit = "stock.picking.in"

    _columns = {
        'invoice_id': fields.many2one(
            'account.invoice', 'Invoice', readonly=True),
    }
