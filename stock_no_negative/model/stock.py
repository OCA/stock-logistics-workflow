# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Luis Torres (luis_t@vauxoo.com)
#
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

from openerp import _, exceptions, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def get_operations_as_action_done(self, cr, uid, ids,
                                      context=None):
        """Get stock.pack.operation from stock move
        Copied from 'action_done' original method

        I don't know if use directly move.linked_move_operation_ids
        or move.pack_operation_ids is a good idea.
        But I prefer use native extract data.
        Move don't exists 'lot_id', then this is necessary to get it
        """

        # Search operations that are linked to the moves
        operations = set()
        for move in self.browse(cr, uid, ids, context=context):
            for link in move.linked_move_operation_ids:
                operations.add(link.operation_id)

        # Sort operations according to entire packages first,
        # then package + lot, package only, lot only
        operations = list(operations)
        # This part not is necessary
        # operations.sort(key=lambda x: (
        #    (x.package_id and not x.product_id) and -4 or 0) \
        #    + (x.package_id and -2 or 0) + (x.lot_id and -1 or 0))
        return operations

    def check_after_action_done(self, cr, uid, operation_or_move,
                          lot_id=None, context=None):
        """
        Method to check operation or move plus lot_id
        easiest inherit cases after action done
        """
        return True

    def check_before_action_done(self, cr, uid, operation_or_move,
                          lot_id=None, context=None):
        """
        Method to check operation or move plus lot_id
        easiest inherit cases before action done
        """
        # TODO: stock_move use product_uom
        self.check_before_done_no_negative(
            cr, uid, operation_or_move.product_id.id,
            operation_or_move.product_uom_id.id,
            operation_or_move.product_qty,
            operation_or_move.location_id.id,
            lot_id=lot_id,
            context=context)
        return True

    def action_done(self, cr, uid, ids, context=None):
        """
        Method to enable check operation or move

        We need this check after of process move to get
        real quantity after of this moves and we need this check
        before of process move to validate with no real quantity
        """
        # operations before done
        operations_before_done = self.get_operations_as_action_done(
            cr, uid, ids, context=context)
        for operation in operations_before_done:
            lot_id = operation.lot_id.id \
                if operation.lot_id \
                else False
            self.check_before_action_done(
                cr, uid, operation, lot_id, context=context)

        res = super(StockMove, self).action_done(
            cr, uid, ids, context=context)

        # operations after done
        operations_after_done = self.get_operations_as_action_done(
            cr, uid, ids, context=context)
        for operation in operations_after_done:
            lot_id = operation.lot_id.id \
                if operation.lot_id \
                else False
            self.check_after_action_done(
                cr, uid, operation, lot_id, context=context)
        return res

    def check_before_done_no_negative(
            self, cr, uid,
            product_id, product_uom, product_qty,
            location_id, lot_id=None,
            context=None):
        """
        Check quantity no negative from a location.
        if product has active check_no_negative and
        location is internal
        Use lot_id if exists to get quantity available
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param product_id: integer with product.product to check
        @param location_id: integer with stock.location to check
        @param lot_id: optional integer with
                       stock.production.lot to check
        @param context: A standard dictionary
        @return: True if quantity available >= 0
                 triggers an exception if quantity available <0
        """
        product_pool = self.pool.get('product.product')
        location_pool = self.pool.get('stock.location')
        lot_pool = self.pool.get('stock.production.lot')
        product_uom_obj = self.pool.get('product.uom')
        product_data = product_pool.read(
            cr, uid,
            [product_id], ['name', 'check_no_negative', 'uom_id'],
            context=context)[0]
        if product_data['check_no_negative']:
            location_data = location_pool.read(
                cr, uid, [location_id],
                ['complete_name', 'usage'],
                context=context)[0]
            if location_data['usage'] == 'internal':
                ctx = context.copy()
                ctx.update({
                    'lot_id': lot_id,
                    'location': location_id,
                    'compute_child': True,
                })
                qty_available_before_done = product_pool.read(
                    cr, uid,
                    [product_id], ['qty_available'],
                    context=ctx)[0]['qty_available']
                default_uom_id = product_data['uom_id'][0]
                qty_computed = product_uom_obj._compute_qty(
                    cr, uid, product_uom, product_qty, default_uom_id)
                qty_available_after_done = qty_available_before_done - qty_computed
                if qty_available_after_done < 0:
                    lot_msg_str = ""
                    if lot_id:
                        lot_data = lot_pool.read(
                            cr, uid,
                            [lot_id], ['name'],
                            context=context)[0]
                        lot_msg_str = _(
                            " with the lot/serial '%s' "
                            ) % lot_data['name']
                    raise exceptions.ValidationError(_(
                        "Product '%s' has active "
                        "'check no negative' \n"
                        "but with this move "
                        "you will have a quantity of "
                        "'%s' \n%sin location \n'%s'"
                        ) % (product_data['name'],
                             qty_available_after_done,
                             lot_msg_str,
                             location_data['complete_name'],))
        return True
