# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2015 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
#            Alex Duan <alex.duan@elico-corp.com>
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
##############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp import netsvc


class StockLocation(orm.Model):
    _name = 'stock.location'
    _inherit = "stock.location"
    _columns = {
        'retention_mode': fields.selection(
            [('retention', _('Retention Mode')), ('thru', _('Thru mode'))],
            _('Retention Mode'),
            required=True,
            help=_("In 'Retention mode' the system wait for the\
                  whole quantity before the stuff is processed.\n" +
                   "In 'Thru mode' the shipped quantity is processed regardless\
                  of the ordered quantity.")
        ),
    }
    _defaults = {
        'retention_mode': 'retention',
    }


class StockPicking(orm.Model):
    _name = 'stock.picking'
    _inherit = "stock.picking"

    def get_move_chain(self, cr, uid, move_id, context=None, move_obj=False):
        '''Recursively get the chained moves
        @return list of the chained moves
        '''
        if not move_obj:
            move_obj = self.pool.get('stock.move')
        move_tbc = move_obj.browse(cr, uid, move_id, context, move_obj)

        # If there is move_dest_id in the chain
        if move_tbc.move_dest_id:
            move_chain = self.get_move_chain(
                cr, uid, move_tbc.move_dest_id.id, context)
        else:
            move_chain = []

        move_chain.append(move_tbc)
        return move_chain

    def copy_pick_chain(self, cr, uid, all_moves, context=None):
        '''Copy all the picking related to this order.

        @return the dictionary: {old_pick_id: new_pick_id}
        '''
        new_picks = {}
        all_chained_moves = []
        sequence_obj = self.pool.get('ir.sequence')

        def _get_sequence_name(seq_obj, pick):
            if pick.type == 'internal':
                name = seq_obj.get(cr, uid, 'stock.picking')
            else:
                name = seq_obj.get(cr, uid, 'stock.picking.' + pick.type)
            return name

        for move in all_moves:
            all_chained_moves.extend(
                self.get_move_chain(cr, uid, move.id, context))

        for move in all_chained_moves:
            if not move.picking_id:
                # TODO handle this kind of exception.
                raise orm.except_orm(
                    _('Data Error'),
                    _('There is no picking relates to this move: ') +
                    '%s' % move.name)
            if move.picking_id.id and (move.picking_id.id not in new_picks):
                pick_tbc = self.browse(cr, uid, move.picking_id.id, context)
                new_note = ((pick_tbc.note if pick_tbc.note else '') +
                            ' Copy of stock.pick[%d].') % move.picking_id.id
                new_pick_id = self.copy(
                    cr, uid, move.picking_id.id,
                    {
                        'state': 'draft',
                        'note': new_note,
                        'name': _get_sequence_name(sequence_obj, pick_tbc),
                        'move_lines': [],
                    })
                new_picks[move.picking_id.id] = new_pick_id

        return new_picks

    def copy_move_chain(
            self, cr, uid, move_id, product_qty, new_picks, context=None, move_obj=False):
        '''Recursively copy the chained move until a location in retention mode or the end.
        @return id of the new first move.
        '''
        if not move_obj:
            move_obj = self.pool.get('stock.move')
        move_tbc = move_obj.browse(cr, uid, move_id, context)
        move_dest_id = False

        # If there is move_dest_id in the chain and the current location is in thru mode,
        # we need to make a copy of that, then use it as new move_dest_id.
        if move_tbc.move_dest_id and \
                move_tbc.location_dest_id.retention_mode == 'thru':
            move_dest_id = self.copy_move_chain(
                cr, uid, move_tbc.move_dest_id.id, product_qty, new_picks, context, move_obj)

        my_picking_id = new_picks.get(move_tbc.picking_id.id, False)

        new_note = ((move_tbc.note if move_tbc.note else '') + ' Copy of stock.move[%d].') % move_id
        new_move_id = move_obj.copy(
            cr, uid, move_id,
            {
                'move_dest_id': move_dest_id,
                'state': 'waiting',
                'note': new_note,
                # Don't inherit child, populate it in next step. The same to next line.
                'move_history_ids': False,
                'move_history_ids2': False,
                'product_qty': product_qty,
                'product_uos_qty': product_qty,
                'picking_id': my_picking_id,
                'price_unit': move_tbc.price_unit,
            })

        # Create the move_history_ids (child) if there is.
        if move_dest_id:
            move_obj.write(
                cr, uid, [new_move_id],
                {'move_history_ids': [(4, move_dest_id)]})
        return new_move_id

    def update_move_chain_pick(self, cr, uid, move_id, vals, new_picks, context=None):
        '''Recursively update the new chained move with the new related picking
            by the first move id until a location in retention mode or the end.

        @return True if ok.
        '''
        move_obj = self.pool.get('stock.move')
        move_tbu = move_obj.browse(cr, uid, move_id, context)

        while True:
            vals.update(picking_id=new_picks[move_tbu.picking_id.id])
            move_obj.write(cr, uid, [move_tbu.id], vals, context)

            if not move_tbu.move_dest_id or move_tbu.location_dest_id.retention_mode != 'thru':
                break

            move_tbu = move_tbu.move_dest_id
        return True

    def update_move_chain(self, cr, uid, move_id, vals, context=None):
        '''Recursively update the old chained move by the first move id
            until a location in retention mode or the end.

        @return True if ok.
        '''
        ids = [move_id]
        move_obj = self.pool.get('stock.move')
        move_tbu = move_obj.browse(cr, uid, move_id, context)

        while move_tbu.move_dest_id and move_tbu.location_dest_id.retention_mode == 'thru':
            ids.append(move_tbu.move_dest_id.id)
            move_tbu = move_tbu.move_dest_id

        move_obj.write(cr, uid, ids, vals, context)
        return True

    def is_pick_not_empty(self, cr, uid, pick_id, move_obj, context=None):
        cpt = move_obj.search(
            cr, uid,
            [('picking_id', '=', pick_id)],
            context=context, count=True)
        return cpt > 0

    def check_production_node_move_chain(
            self, cr, uid, move_tbc, context=None):
        if move_tbc.location_id.usage == 'production':
            return True

        if move_tbc.move_dest_id:
            if self.check_production_node_move_chain(
                    cr, uid, move_tbc.move_dest_id, context):
                return True
        return False

    def has_production_mode(self, cr, uid, all_moves, context=None):
        for move in all_moves:
            if self.check_production_node_move_chain(cr, uid, move, context):
                return True
        return False

    # FIXME: needs refactoring, this code is partially duplicated in stock_move.
    # do_partial()!
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, partner_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            complete, too_many, too_few = [], [], []
            # Elico
            all_moves = []
            move_product_qty, prodlot_ids, partial_qty, uos_qty, product_uoms = {}, {}, {}, {}, {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s' % (move.id), {})
                product_qty = partial_data.get('product_qty', 0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get(
                    'product_uom', move.product_uom.id)
                product_price = partial_data.get('product_price', 0.0)
                product_currency = partial_data.get('product_currency', False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(
                    cr, uid, product_uoms[move.id],
                    product_qty, move.product_uom.id)
                uos_qty[move.id] = move.product_id._compute_uos_qty(
                    product_uom, product_qty,
                    move.product_uos) if product_qty else 0.0
                all_moves.append(move)
                if move.product_qty == partial_qty[move.id]:
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)

                if (pick.type == 'in') and \
                        (move.product_id.cost_method == 'average'):
                    # Record the values that were chosen in the wizard,
                    # so they can be
                    # used for average price computation
                    # and inventory valuation
                    move_obj.write(
                        cr, uid, [move.id],
                        {'price_unit': product_price,
                         'price_currency_id': product_currency})

            # check if there is a production location in the chain
            if self.has_production_mode(cr, uid, all_moves, context=context):
                res[pick.id] = super(StockPicking, self).do_partial(
                    cr, uid, [pick.id], partial_datas, context=context)
            else:
                new_picks = self.copy_pick_chain(cr, uid, all_moves, context)
                for move in too_few:
                    product_qty = move_product_qty[move.id]
                    if product_qty != 0:
                        if product_qty != 0:
                            """Copy not only one move, but all the moves
                            where the destination location is in THRU MODE """
                            new_move_id = self.copy_move_chain(
                                cr, uid, move.id, product_qty,
                                new_picks, context)

                            prodlot_id = prodlot_ids[move.id]
                            if prodlot_id:
                                self.update_move_chain(cr, uid, new_move_id, {
                                    'prodlot_id': prodlot_id,
                                }, context)

                            """Update the old moves with
                                the remaining quantity"""
                            self.update_move_chain(cr, uid, move.id, {
                                'product_qty': move.product_qty - product_qty,
                                # TODO: put correct uos_qty
                                'product_uos_qty': move.product_qty - product_qty,
                            }, context)

                        else:
                            move_obj.write(
                                cr, uid, [move.id],
                                {
                                    'states': 'waiting',
                                })
                for move in complete:
                        defaults = {}
                        if prodlot_ids.get(move.id):
                            defaults.update(prodlot_id=prodlot_id)

                        if move.location_id.retention_mode == 'thru':
                            self.update_move_chain_pick(
                                cr, uid, move.id, defaults, new_picks, context)
                        else:
                            move_obj.write(
                                cr, uid, [move.id],
                                {'picking_id': new_picks[move.picking_id.id]},
                                context)
                for move in too_many:
                    product_qty = move_product_qty[move.id]
                    defaults = {}
                    defaults_1st_move = {
                        'picking_id': new_picks[move.picking_id.id],
                        'product_qty': product_qty,
                        # TODO: put correct uos_qty
                        'product_uos_qty': product_qty,
                    }
                    prodlot_id = prodlot_ids.get(move.id)
                    if prodlot_ids.get(move.id):
                        defaults.update(prodlot_id=prodlot_id)
                        defaults_1st_move.update(prodlot_id=prodlot_id)

                    move_obj.write(
                        cr, uid, [move.id], defaults_1st_move, context)
                    if move.location_id.retention_mode == 'thru':
                        self.update_move_chain_pick(
                            cr, uid, move.id, defaults, new_picks, context)
                    else:
                        move_obj.write(
                            cr, uid, [move.id],
                            {'picking_id': new_picks[move.picking_id.id]},
                            context)

                # At first we confirm the new pickings (if necessary)
                for old_pick, new_pick in new_picks.iteritems():

                    # check if the old pick is empty
                    if not self.is_pick_not_empty(
                            cr, uid, old_pick, move_obj, context):
                        self.unlink(cr, uid, [old_pick])
                    # check if the new pick is not empty
                    if self.is_pick_not_empty(
                            cr, uid, new_pick, move_obj, context):
                        if self.is_pick_not_empty(
                                cr, uid, old_pick, move_obj, context):
                            self.write(
                                cr, uid, [old_pick],
                                {'backorder_id': new_pick})
                            wf_service.trg_validate(
                                uid, 'stock.picking', new_pick,
                                'button_confirm', cr)
                    else:
                        self.unlink(cr, uid, [new_pick])

                    if new_pick:
                        delivered_pack_id = new_pick
                    else:
                        delivered_pack_id = old_pick
                    delivered_pack = self.browse(
                        cr, uid, delivered_pack_id, context=context)
                    res[pick.id] = {'delivered_picking': delivered_pack.id}

                pick.refresh()
                # Here we set the moves as "assigned"
                pick_hack = self.browse(cr, uid, pick.id, context=context)
                for move in pick_hack.backorder_id.move_lines:
                    move_obj.action_assign(cr, uid, [move.id])

                # The pick is set as "confirmed" then "done"
                wf_service.trg_validate(
                    uid, 'stock.picking',
                    new_picks[pick.id], 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)

                pick.refresh()
                # Finally we set the next pick as "assigned"
                pick_hack = self.browse(cr, uid, pick.id, context=context)
                for move in pick_hack.backorder_id.move_lines:
                    if move.move_dest_id.picking_id and self.test_assigned(
                            cr, uid, [move.move_dest_id.picking_id.id]):
                        self.action_assign_wkf(
                            cr, uid, [move.move_dest_id.picking_id.id],
                            context=context)
        return res


class StockMove(orm.Model):
    _name = "stock.move"
    _inherit = "stock.move"

    def copy_move_chain(self, cr, uid, move_id, product_qty, context=None):
        '''Recursively copy the chained move until a location in retention mode or the end.
        @return id of the new first move.
        '''
        move_tbc = self.browse(cr, uid, move_id, context)
        move_dest_id = False
        # If there is move_dest_id in the chain and the current location is in thru mode,
        # we need to make a copy of that, then use it as new move_dest_id.
        if move_tbc.move_dest_id and move_tbc.location_dest_id.retention_mode == 'thru':
            move_dest_id = self.copy_move_chain(
                cr, uid, move_tbc.move_dest_id.id, product_qty, context)

        new_note = ((move_tbc.note if move_tbc.note else '') + ' Copy of stock.move[%d].') % move_id
        new_move_id = self.copy(
            cr, uid, move_id,
            {
                'move_dest_id': move_dest_id,
                'state': 'waiting',
                'note': new_note,
                # Don't inherit child, populate it in next step. The same to next line.
                'move_history_ids': False,
                'move_history_ids2': False,
                'product_qty': product_qty,
                'product_uos_qty': product_qty,
                'picking_id': move_tbc.picking_id.id,
                'price_unit': move_tbc.price_unit,
                'auto_validate': False
            })
        # Create the move_history_ids (child) if there is.
        if move_dest_id:
            self.write(cr, uid, [new_move_id], {'move_history_ids': [(4, move_dest_id)]})
        return new_move_id

    def update_move_chain(self, cr, uid, move_id, vals, context=None):
        '''Recursively update the chained move by the first move id
        until a location in retention mode or the end.

        @return True if ok.
        '''

        if isinstance(move_id, list):
            move_id = move_id[0]
        ids = [move_id]
        move_tbu = self.browse(cr, uid, move_id, context)

        while move_tbu.move_dest_id and move_tbu.location_dest_id.retention_mode == 'thru':
            ids.append(move_tbu.move_dest_id.id)
            move_tbu = move_tbu.move_dest_id

        self.write(cr, uid, ids, vals, context)
        return True

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial pickings and moves done.
        @param partial_datas: Dictionary containing details of partial picking
                          like partner_id, address_id, delivery_date, delivery
                          moves with product_id, product_qty, uom
        """
        res = {}
        picking_obj = self.pool.get('stock.picking')
        wf_service = netsvc.LocalService("workflow")

        if context is None:
            context = {}

        complete, too_many, too_few = [], [], []
        move_product_qty = {}
        prodlot_ids = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ('done', 'cancel'):
                continue
            partial_data = partial_datas.get('move%s' % (move.id), False)
            assert partial_data, _('Missing partial picking data for move #%s') % (move.id)
            product_qty = partial_data.get('product_qty', 0.0)
            move_product_qty[move.id] = product_qty
            product_price = partial_data.get('product_price', 0.0)
            product_currency = partial_data.get('product_currency', False)
            prodlot_ids[move.id] = partial_data.get('prodlot_id')
            if move.product_qty == product_qty:
                complete.append(move)
            elif move.product_qty > product_qty:
                too_few.append(move)
            else:
                too_many.append(move)

            # Average price computation
            if (move.picking_id.type == 'in') and (move.product_id.cost_method == 'average'):
                    # Record the values that were chosen in the wizard, so they can be
                    # used for inventory valuation if real-time valuation is enabled.
                    self.write(
                        cr, uid, [move.id],
                        {'price_unit': product_price,
                         'price_currency_id': product_currency}
                    )

        for move in too_few:
            product_qty = move_product_qty[move.id]
            if product_qty != 0:
                prodlot_id = prodlot_ids[move.id]
                if prodlot_id:
                    self.update_move_chain(
                        cr, uid, [move.id],
                        {'prodlot_id': prodlot_id},
                        context)

                """Copy not only one move, but all the moves where the
                    destination location is in THRU MODE """
                new_move_id = self.copy_move_chain(cr, uid, move.id, product_qty, context)
                complete.append(self.browse(cr, uid, new_move_id))

                """Update not only one move,
                    but all the moves where the destination location is in THRU MODE """
                self.update_move_chain(
                    cr, uid, [move.id],
                    {'product_qty': move.product_qty - product_qty,
                     'product_uos_qty': move.product_qty - product_qty},
                    context)
            else:
                self.write(
                    cr, uid, [move.id],
                    {
                        'states': 'waiting',
                    })

        for move in too_many:
            self.write(
                cr, uid, [move.id],
                {'product_qty': move.product_qty,
                 'product_uos_qty': move.product_qty}
            )
            complete.append(move)
        for move in complete:
            if prodlot_ids.get(move.id):
                self.write(cr, uid, [move.id], {'prodlot_id': prodlot_ids.get(move.id)})
            self.action_done(cr, uid, [move.id], context=context)
            if move.picking_id.id:
                # TOCHECK : Done picking if all moves are done
                cr.execute("""
                    SELECT move.id FROM stock_picking pick
                    RIGHT JOIN stock_move move ON move.picking_id = pick.id AND move.state = %s
                    WHERE pick.id = %s""", ('done', move.picking_id.id))
                res = cr.fetchall()
                if len(res) == len(move.picking_id.move_lines):
                    picking_obj.action_move(cr, uid, [move.picking_id.id])
                    wf_service.trg_validate(
                        uid, 'stock.picking', move.picking_id.id, 'button_done', cr)
        return [move.id for move in complete]
