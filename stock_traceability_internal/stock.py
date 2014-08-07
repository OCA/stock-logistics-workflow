# -*- coding: utf-8 -*-
#
#
#    This module is copyright (C) 2013 Numérigraphe SARL. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp.osv import orm


class StockMove(orm.Model):
    _inherit = 'stock.move'

    def _check_internal_tracking(self, cr, uid, ids, context=None):
        """Checks if production lot is assigned to stock move or not.
        @return: True or False
        """
        for move in self.browse(cr, uid, ids, context=context):
            if (not move.prodlot_id
                    and move.state == 'done'
                    and move.product_id.track_internal
                    and (
                        move.location_id.usage == 'internal'
                        or move.location_dest_id.usage == 'internal')
                    # We still let users correct wrong moves with inventories
                    and move.location_id.usage != 'inventory'
                    and move.location_dest_id.usage != 'inventory'
                    # We don't block pseudo-moves
                    and move.product_qty != 0.0):
                return False
        return True

    _constraints = [
        (_check_internal_tracking,
            'You must assign a serial number for this product.',
            ['prodlot_id']),
    ]
