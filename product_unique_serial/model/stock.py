# -*- coding: utf-8 -*-

from openerp import _, api, fields, exceptions, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.one
    @api.depends('quant_ids')
    def _get_last_location_id(self):
        last_quant_data = self.env['stock.quant'].search_read(
            [('id', 'in', self.quant_ids.ids)],
            ['location_id'],
            order='in_date DESC, id DESC',
            limit=1)
        if last_quant_data:
            self.last_location_id = last_quant_data[0][
                'location_id'][0]
        else:
            self.last_location_id = False

    last_location_id = fields.Many2one(
        'stock.location',
        string="Last location",
        compute='_get_last_location_id',
        store=True)  # TODO: Fix fails recomputed

    # Overwrite field to deny create serial number duplicated
    ref = fields.Char('Internal Reference',
                      help="Internal reference number"
                           " in this case it"
                           " is same of manufacturer's"
                           " serial number",
                      related="name", store=True, readonly=True)


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

    def action_done(self, cr, uid, ids, context=None):
        """
        Method to enable check unicity on quantity on hand

        We need this check after of process move to get
        real quantity after of this moves.
        """
        res = super(StockMove, self).action_done(
            cr, uid, ids, context=context)
        operations = self.get_operations_as_action_done(
            cr, uid, ids, context=context)
        for operation in operations:
            lot_id = operation.lot_id.id \
                if operation.lot_id \
                else False
            self.check_unicity_qty_available(
                cr, uid, operation, lot_id, context=context)
        return res

    def check_unicity_move_qty(self, cr, uid, ids, context=None):
        """
        Check move quantity to verify that has qty = 1
        if 'lot unique' is ok on product
        """
        if not isinstance(ids, list):
            ids = [ids]
        for move in self.browse(cr, uid, ids, context=context):
            if move.product_id.lot_unique_ok:
                for move_operation in \
                        move.linked_move_operation_ids:
                    if abs(move_operation.qty) > 1:
                        raise exceptions.ValidationError(_(
                            "Product '%s' has active"
                            " 'unique lot' "
                            "but has qty > 1"
                            ) % (move.product_id.name))

    def check_unicity_qty_available(self, cr, uid, operation_or_move,
                                    lot_id,
                                    context=None):
        """
        Check quantity on hand to verify that has qty = 1
        if 'lot unique' is ok on product
        """
        if operation_or_move.product_id.lot_unique_ok and lot_id:
            ctx = context.copy()
            ctx.update({'lot_id': lot_id})
            product_ctx = self.pool.get('product.product').browse(
                cr, uid, [operation_or_move.product_id.id],
                context=ctx)[0]
            qty = product_ctx.qty_available
            if abs(qty) > 1:
                lot = self.pool.get('stock.production.lot').browse(
                    cr, uid, [lot_id])[0]
                raise exceptions.ValidationError(_(
                    "Product '%s' has active "
                    "'unique lot'\n"
                    "but with this move "
                    "you will have a quantity of "
                    "'%s' in lot '%s'"
                    ) % (operation_or_move.product_id.name, qty, lot.name))

    # def check_tracking(self, cr, uid, move, lot_id, context=None):
        # res = super(StockMove, self).check_tracking(
        #    cr, uid, move, lot_id, context=context)
        # self.check_unicity_move_qty(cr, uid, [move.id], context=context)
        # return res
