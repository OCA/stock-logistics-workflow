# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (c) 2013 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                    Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, orm


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def _get_return_ids(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for picking in self.browse(cr, uid, ids, context=context):
            for line in picking.move_lines:
                return_ids = []
                if line.state == 'done':
                    for rec in line.move_history_ids2:
                        if (
                            rec.location_dest_id.id == line.location_id.id and
                            rec.location_id.id == line.location_dest_id.id
                        ):
                            return_ids.append(rec.picking_id.id)
                result[picking.id] = return_ids
        return result

    _columns = {
        'return_ids': fields.function(_get_return_ids,
                                      relation='stock.picking',
                                      string="Return pickings",
                                      type='many2many'),
    }


class stock_picking_out(orm.Model):
    _inherit = 'stock.picking.out'

    def _get_return_ids(self, cr, uid, ids, name, arg, context=None):
        return super(stock_picking_out, self)._get_return_ids(cr, uid, ids,
                                                              name, arg,
                                                              context=context)

    _columns = {
        'return_ids': fields.function(_get_return_ids,
                                      relation='stock.picking',
                                      string="Return pickings",
                                      type='many2many'),
    }


class stock_picking_in(orm.Model):
    _inherit = 'stock.picking.in'

    def _get_return_ids(self, cr, uid, ids, name, arg, context=None):
        return super(stock_picking_out, self)._get_return_ids(cr, uid, ids,
                                                              name, arg,
                                                              context=context)

    _columns = {
        'return_ids': fields.function(_get_return_ids,
                                      relation='stock.picking',
                                      string="Return pickings",
                                      type='many2many'),
    }
