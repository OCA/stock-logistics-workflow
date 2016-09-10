# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016, Eska Yazılım ve Danışmanlık A.Ş.
#    http://www.eskayazilim.com.tr
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
##############################################################################
from openerp import api, _, exceptions, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _quant_create(self, qty, move, lot_id=False, owner_id=False,
                      src_package_id=False, dest_package_id=False,
                      force_location_from=False, force_location_to=False):
        if move.product_id.check_no_negative \
                and move.location_id.usage == 'internal':
            lot_msg_str = ""
            if lot_id:
                lot = self.env['stock.production.lot'].browse(lot_id)
                lot_msg_str = _(" with the lot/serial '%s' ") % lot.name
            raise exceptions.ValidationError(_(
                "Product '%s' has active "
                "'check no negative' \n"
                "but with this move "
                "you will have a quantity of "
                "'%s' \n%sin location \n'%s'"
            ) % (move.product_id.name,
                 move.product_id.qty_available - move.product_uom_qty,
                 lot_msg_str,
                 move.location_id.name,))
        return super(StockQuant, self)._quant_create(
            qty, move, lot_id=lot_id, owner_id=owner_id,
            src_package_id=src_package_id, dest_package_id=dest_package_id,
            force_location_from=force_location_from,
            force_location_to=force_location_to)

