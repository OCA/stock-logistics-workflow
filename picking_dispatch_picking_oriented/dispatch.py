# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle, Romain Deheele
#    Copyright 2014 Camptocamp SA
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
#############################################################################
import logging
import time
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.osv import orm, fields
from openerp.tools.translate import _
_logger = logging.getLogger(__name__)


class stock_partial_picking(orm.TransientModel):
    _inherit = "stock.partial.picking"

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(stock_partial_picking, self).default_get(cr, uid, fields,
                                                             context=context)
        picking_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not picking_ids or len(picking_ids) != 1:
            """ Partial Picking Processing may only be done
            for one picking at a time"""
            return res
        assert active_model in ('stock.picking', 'stock.picking.in', 'stock.picking.out'), 'Bad context propagation'
        picking_id, = picking_ids
        if 'picking_id' in fields:
            res.update(picking_id=picking_id)
        if 'move_ids' in fields:
            picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
            moves = [self._partial_move_for(cr, uid, m)
                     for m in picking.move_lines
                     if (m.state not in ('done', 'cancel')
                         and not (m.dispatch_id and m.dispatch_id.state != 'done'))]
            res.update(move_ids=moves)
        if 'date' in fields:
            res.update(date=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        return res


class stock_partial_move(orm.TransientModel):
    _inherit = 'stock.partial.move'

    def do_partial(self, cr, uid, ids, context=None):
        # no call to super!
        assert len(ids) == 1, 'Partial move processing may only be done one form at a time.'
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_data = {
            'delivery_date': partial.date
        }
        moves_ids = []
        for move in partial.move_ids:
            if not move.move_id:
                raise orm.except_orm(_('Warning !'), _("You have manually created product lines, please delete them to proceed"))
            move_id = move.move_id.id
            partial_data['move%s' % (move_id)] = {
                'product_id': move.product_id.id,
                'product_qty': move.quantity,
                'product_uom': move.product_uom.id,
                'prodlot_id': move.prodlot_id.id,
            }
            moves_ids.append(move_id)
            if (move.move_id.picking_id.type == 'in') and (move.product_id.cost_method == 'average'):
                partial_data['move%s' % (move_id)].update(product_price=move.cost,
                                                          product_currency=move.currency.id)
        #in classic context, we close wizard pop-up.
        #in picking dispatch context, we need to display the new created dispatch
        res = self.pool.get('stock.move').do_partial(cr, uid, moves_ids, partial_data, context=context)
        if context and 'partial_via_dispatch' in context:
            return res
        return {'type': 'ir.actions.act_window_close'}


class PickingDispatch(orm.Model):
    _inherit = 'picking.dispatch'

    def action_done(self, cr, uid, ids, context=None):
        """Open the partial picking wizard"""
        if not ids:
            return True
        if context is None:
            context = {}
        ctx = context.copy()
        ctx.update({
            'partial_via_dispatch': True,
        })
        move_obj = self.pool['stock.move']
        move_ids = move_obj.search(cr, uid, [('dispatch_id', 'in', ids)], context=ctx)
        return move_obj.action_partial_move(cr, uid, move_ids, context=ctx)


class StockMove(orm.Model):
    _inherit = 'stock.move'

    _columns = {
        'dispatch_state': fields.related('dispatch_id', 'state',
                                         type='char',
                                         relation='picking.dispatch',
                                         string='Dispatch State',
                                         readonly=True),
    }

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.

        Inherited to allow the use of do_partial_via_dispatch()
        instead of do_partial(), switch is done with
        a 'partial_via_dispatch' key in the context.

        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, address_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        if context.get('partial_via_dispatch'):
            return self.do_partial_via_dispatch(
                cr, uid, ids, partial_datas, context=context)
        else:
            return super(StockMove, self).do_partial(
                cr, uid, ids, partial_datas, context=context)

    def do_partial_via_dispatch(self, cr, uid, ids, partial_datas, context=None):
        """ Makes picking dispatch done, split moves between ok and other in backorders.
        @param partial_datas: Dictionary containing details of partial picking
                          like partner_id, delivery_date, delivery
                          moves with product_id, product_qty, uom
        """
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        pricetype_obj = self.pool.get('product.price.type')
        uom_obj = self.pool.get('product.uom')
        dispatch_obj = self.pool.get('picking.dispatch')

        if context is None:
            context = {}

        complete, too_many, too_few = [], [], []
        move_product_qty = {}
        prodlot_ids = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ('done', 'cancel'):
                continue
            partial_data = partial_datas.get('move%s' % (move.id), False)
            assert partial_data, _('Missing partial picking data for move #%s.') % (move.id)
            product_qty = partial_data.get('product_qty', 0.0)
            move_product_qty[move.id] = product_qty
            product_uom = partial_data.get('product_uom', False)
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
                product = product_obj.browse(cr, uid, move.product_id.id)
                move_currency_id = move.company_id.currency_id.id
                context['currency_id'] = move_currency_id
                qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
                price_type_id = pricetype_obj.search(cr, uid,
                                                     [('field', '=', 'standard_price')],
                                                     context=context)[0]
                price_type = pricetype_obj.browse(cr, uid, price_type_id, context=context)
                price_type_currency_id = price_type.currency_id.id
                if qty > 0:
                    new_price = currency_obj.compute(cr, uid, product_currency,
                                                     move_currency_id, product_price, round=False)
                    new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                                       product.uom_id.id)
                    if product.qty_available <= 0:
                        new_std_price = new_price
                    else:
                        # Get the standard price
                        amount_unit = product.price_get('standard_price', context=context)[product.id]
                        # Here we must convert the new price computed in the currency of the price_type
                        # of the product (e.g. company currency: EUR, price_type: USD)
                        # The current value is still in company currency at this stage
                        new_std_price = ((amount_unit * product.qty_available)
                                         + (new_price * qty))/(product.qty_available + qty)
                    # Convert the price in price_type currency
                    new_std_price = currency_obj.compute(
                        cr, uid, move_currency_id,
                        price_type_currency_id, new_std_price)
                    # Write the field according to price type field
                    product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

                    # Record the values that were chosen in the wizard, so they can be
                    # used for inventory valuation if real-time valuation is enabled.
                    self.write(cr, uid, [move.id],
                               {'price_unit': product_price,
                                'price_currency_id': product_currency,
                                })

        for move in too_few:
            product_qty = move_product_qty[move.id]
            if product_qty != 0:
                defaults = {
                    'product_qty': product_qty,
                    'product_uos_qty': product_qty,
                    'picking_id': move.picking_id.id,
                    'state': 'assigned',
                    'move_dest_id': move.move_dest_id.id,
                    'price_unit': move.price_unit,
                    }
                prodlot_id = prodlot_ids[move.id]
                if prodlot_id:
                    defaults.update(prodlot_id=prodlot_id)
                new_move = self.copy(cr, uid, move.id, defaults)
                complete.append(self.browse(cr, uid, new_move))
            self.write(cr, uid, [move.id],
                       {'product_qty': move.product_qty - product_qty,
                        'product_uos_qty': move.product_qty - product_qty,
                        'prodlot_id': False,
                        'tracking_id': False,
                        })

        for move in too_many:
            self.write(cr, uid, [move.id],
                       {'product_qty': move.product_qty,
                        'product_uos_qty': move.product_qty,
                        })
            complete.append(move)

        for move in complete:
            if prodlot_ids.get(move.id):
                self.write(cr, uid, [move.id], {'prodlot_id': prodlot_ids.get(move.id)})

        # in complete_move_ids, we have:
        # * moves that were fully processed
        # * newly created moves belonging
        #   to the same dispatch as the original move
        # so the difference between the original set of moves
        # and the complete_moves is the set of unprocessed moves
        dispatch_id = context['active_id']
        ids = self.search(cr, uid,
                          [('dispatch_id', '=', context['active_id'])],
                          context=context)
        complete_move_ids = [x.id for x in complete]
        unprocessed_move_ids = set(ids) - set(complete_move_ids)
        if unprocessed_move_ids:
            new_dispatch_id = dispatch_obj.copy(cr, uid, dispatch_id,
                                                {'backorder_id': dispatch_id})
            self.write(cr, uid, complete_move_ids,
                       {'dispatch_id': dispatch_id})
            self.write(cr, uid, list(unprocessed_move_ids),
                       {'dispatch_id': new_dispatch_id})
            dispatch_obj.write(cr, uid, [dispatch_id], {'state': 'done'},
                               context=context)
            return {
                'domain': str([('id', '=', dispatch_id)]),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'picking.dispatch',
                'type': 'ir.actions.act_window',
                'context': context,
                'res_id': dispatch_id,
            }
        else:
            dispatch_obj.write(cr, uid, [dispatch_id], {'state': 'done'},
                               context=context)
            return {'type': 'ir.actions.act_window_close'}
