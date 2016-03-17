# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Vauxoo
#    Author: Moisés Lopez, Osval Reyes
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
from openerp import _, api, exceptions, models


class StockMove(models.Model):

    """
    Stock Move
    """
    _inherit = 'stock.move'

    @api.model
    def check_after_action_done(self, operation_or_move):
        super(StockMove, self).\
            check_after_action_done(operation_or_move)
        return self.check_unicity_qty_available(operation_or_move)

    @api.multi
    def check_unicity_move_qty(self):
        """
        Check move quantity to verify that has qty = 1
        if 'lot unique' is ok on product
        """
        for move in self:
            if move.product_id.lot_unique_ok:
                for move_operation in \
                        move.linked_move_operation_ids:
                    if abs(move_operation.qty) > 1:
                        raise exceptions.ValidationError(_(
                            "Product '%s' has active"
                            " 'unique lot' "
                            "but has qty > 1"
                        ) % (move.product_id.name))

    @api.model
    def check_unicity_qty_available(self, operation_or_move):
        """
        Check quantity on lot to verify that has qty = 1
        if 'lot unique' is ok on product
        """
        lot_id = operation_or_move.lot_id
        if operation_or_move.product_id.lot_unique_ok and lot_id:
            qty = sum([x.qty for x in operation_or_move.lot_id.quant_ids])
            if not 0 <= qty <= 1:
                import pdb; pdb.set_trace()
                raise exceptions.ValidationError(_(
                    "Product '%s' has active "
                    "'unique lot'\n"
                    "but with this move "
                    "you will have a quantity of "
                    "'%s' in lot '%s'"
                ) % (operation_or_move.product_id.name, qty, lot_id.name))
        return True

    @api.model
    def check_tracking(self, move, lot_id):
        res = super(StockMove, self).check_tracking(move, lot_id)
        self.check_unicity_move_qty()
        return res
