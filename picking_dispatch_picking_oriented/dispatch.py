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
from openerp import netsvc
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.float_utils import float_compare
from openerp.osv import orm, fields, osv
from openerp.tools.translate import _
_logger = logging.getLogger(__name__)


class stock_partial_picking(orm.TransientModel):
    _inherit = "stock.partial.picking"

    _columns = {
        'carrier_id': fields.many2one('delivery.carrier', 'Carrier'),
    }

    def default_get(self, cr, uid, fields, context=None):
        """override to:
            - add filter on showed moves
            - fill carrier_id"""
        if context is None:
            context = {}
        res = super(stock_partial_picking, self).default_get(cr, uid, fields,
                                                             context=context)
        picking_ids = context.get('active_ids', [])
        active_model = context.get('active_model')
        picking_obj = self.pool.get('stock.picking')

        if not picking_ids or len(picking_ids) != 1:
            """ Partial Picking Processing may only be done
            for one picking at a time"""
            return res
        assert active_model in ('stock.picking', 'stock.picking.in', 'stock.picking.out'), 'Bad context propagation'
        picking_id, = picking_ids
        if 'picking_id' in fields:
            res.update(picking_id=picking_id)
        if 'move_ids' in fields:
            picking = picking_obj.browse(cr, uid, picking_id, context=context)
            moves = [self._partial_move_for(cr, uid, m)
                     for m in picking.move_lines
                     if (m.state not in ('done', 'cancel')
                         and not (m.dispatch_id and
                                  m.dispatch_id.state != 'done'))]
            res.update(move_ids=moves)
        if 'date' in fields:
            res.update(date=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        if 'carrier_id' in fields:
            picking = picking_obj.browse(cr, uid, picking_id, context=context)
            res.update(carrier_id=picking.carrier_id.id)
        return res

    def do_partial(self, cr, uid, ids, context=None):
        """override to just add carrier_id in partial_data"""
        assert len(ids) == 1, 'Partial picking processing may only be done one at a time.'
        stock_picking = self.pool.get('stock.picking')
        stock_move = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_data = {
            'delivery_date': partial.date,
            'carrier_id': partial.carrier_id and partial.carrier_id.id or False
        }
        picking_type = partial.picking_id.type

        for wizard_line in partial.move_ids:
            line_uom = wizard_line.product_uom
            move_id = wizard_line.move_id.id

            #Quantity must be Positive
            if wizard_line.quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Please provide proper Quantity.'))

            #Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
            qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)

            if line_uom.factor and line_uom.factor != 0:
                if float_compare(qty_in_line_uom, wizard_line.quantity, precision_rounding=line_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning!'), _('The unit of measure rounding does not allow you to ship "%s %s", only rounding of "%s %s" is accepted by the Unit of Measure.') % (wizard_line.quantity, line_uom.name, line_uom.rounding, line_uom.name))
            if move_id:
                #Check rounding Quantity.ex.
                #picking: 1kg, uom kg rounding = 0.01 (rounding to 10g),
                #partial delivery: 253g
                #=> result= refused, as the qty left on picking would be 0.747kg and only 0.75 is accepted by the uom.
                initial_uom = wizard_line.move_id.product_uom
                #Compute the quantity for respective wizard_line in the initial uom
                qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
                without_rounding_qty = (wizard_line.quantity / line_uom.factor) * initial_uom.factor
                if float_compare(qty_in_initial_uom, without_rounding_qty, precision_rounding=initial_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning!'), _('The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only rounding of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, wizard_line.move_id.product_qty - without_rounding_qty, initial_uom.name, initial_uom.rounding, initial_uom.name))
            else:
                seq_obj_name = 'stock.picking.' + picking_type
                move_id = stock_move.create(cr, uid, {'name': self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
                                                      'product_id': wizard_line.product_id.id,
                                                      'product_qty': wizard_line.quantity,
                                                      'product_uom': wizard_line.product_uom.id,
                                                      'prodlot_id': wizard_line.prodlot_id.id,
                                                      'location_id': wizard_line.location_id.id,
                                                      'location_dest_id': wizard_line.location_dest_id.id,
                                                      'picking_id': partial.picking_id.id
                                                      }, context=context)
                stock_move.action_confirm(cr, uid, [move_id], context)
            partial_data['move%s' % (move_id)] = {
                'product_id': wizard_line.product_id.id,
                'product_qty': wizard_line.quantity,
                'product_uom': wizard_line.product_uom.id,
                'prodlot_id': wizard_line.prodlot_id.id,
            }
            if (picking_type == 'in') and (wizard_line.product_id.cost_method == 'average'):
                partial_data['move%s' % (wizard_line.move_id.id)].update(product_price=wizard_line.cost,
                                                                         product_currency=wizard_line.currency.id)
        stock_picking.do_partial(cr, uid, [partial.picking_id.id], partial_data, context=context)
        return {'type': 'ir.actions.act_window_close'}


class stock_partial_move(orm.TransientModel):
    _inherit = 'stock.partial.move'

    def do_partial(self, cr, uid, ids, context=None):
        """override to don't close window if the context is 'partial_via_dispatch'"""
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
        """Override to indicate 'partial_via_dispatch' context"""
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


class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Override to:
            - pass carrier_id information on done picking
            - in case of shortage :
                - copies are the moves in state 'done', we need to pass them the current dispatch id
                - undone moves are the original moves:
                    - we need to pass them the id of dispatch backorder if it exists,
                    - we need to pass False if there is no dispatch backorder
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        pricetype_obj = self.pool.get('product.price.type')
        sequence_obj = self.pool.get('ir.sequence')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s' % (move.id), {})
                product_qty = partial_data.get('product_qty', 0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom', False)
                product_price = partial_data.get('product_price', 0.0)
                product_currency = partial_data.get('product_currency', False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
                if move.product_qty == partial_qty[move.id]:
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)

                # Average price computation
                if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
                    price_type_id = pricetype_obj.search(cr, uid,
                                                         [('field', '=', 'standard_price')],
                                                         context=context)[0]
                    price_type = pricetype_obj.browse(cr, uid, price_type_id, context=context)
                    price_type_currency_id = price_type.currency_id.id

                    if product.id not in product_avail:
                        # keep track of stock on hand including processed lines not yet marked as done
                        product_avail[product.id] = product.qty_available

                    if qty > 0:
                        # New price in company currency
                        new_price = currency_obj.compute(cr, uid, product_currency,
                                                         move_currency_id, product_price, round=False)
                        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                                           product.uom_id.id)
                        if product_avail[product.id] <= 0:
                            product_avail[product.id] = 0
                            new_std_price = new_price
                        else:
                            # Get the standard price
                            amount_unit = product.price_get('standard_price', context=context)[product.id]
                            # Here we must convert the new price computed in the currency of the price_type
                            # of the product (e.g. company currency: EUR, price_type: USD)
                            # The current value is still in company currency at this stage
                            new_std_price = ((amount_unit * product_avail[product.id])
                                             + (new_price * qty))/(product_avail[product.id] + qty)
                        # Convert the price in price_type currency
                        new_std_price = currency_obj.compute(
                            cr, uid, move_currency_id,
                            price_type_currency_id, new_std_price)
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        move_obj.write(cr, uid, [move.id], {
                            'price_unit': product_price,
                            'price_currency_id': product_currency
                        })
                        product_avail[product.id] += qty

            for move in too_few:
                product_qty = move_product_qty[move.id]
                if not new_picking:
                    new_picking_name = pick.name
                    self.write(cr, uid, [pick.id], {
                        'name': sequence_obj.get(cr, uid, 'stock.picking.%s' % (pick.type)),
                    })
                    new_picking = self.copy(cr, uid, pick.id, {
                        'name': new_picking_name,
                        'move_lines': [],
                        'state': 'draft',
                        'carrier_id': 'carrier_id' in partial_datas and partial_datas['carrier_id'],
                    })
                if product_qty != 0:
                    defaults = {
                        'product_qty': product_qty,
                        'product_uos_qty': product_qty,  # TODO: put correct uos_qty
                        'picking_id': new_picking,
                        'state': 'assigned',
                        'move_dest_id': move.move_dest_id.id,
                        'price_unit': move.price_unit,
                        'product_uom': product_uoms[move.id],
                        'dispatch_id': move.dispatch_id and move.dispatch_id.id
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    # the copy will be a done move, it has to attached to the current dispatch
                    move_obj.copy(cr, uid, move.id, defaults)
                move_vals = {
                    'product_qty': move.product_qty - partial_qty[move.id],
                    'product_uos_qty': move.product_qty - partial_qty[move.id],  # TODO: put correct uos_qty
                    'prodlot_id': False,
                    'tracking_id': False,
                }
                # 2 cases of shortage context:
                if move.dispatch_id:
                    dispatch_obj = self.pool['picking.dispatch']
                    new_dispatch_id = dispatch_obj.search(cr, uid, [('backorder_id', '=', move.dispatch_id.id),
                                                                    ('state', '=', 'draft')], context=context)
                    # we have anticipated the shortage, a backorder dispatch exists, we can attach the move on it
                    if new_dispatch_id:
                        move_vals['dispatch_id'] = new_dispatch_id[0]
                    # we have not anticipated (broken products,...), the move will be not attached to a dispatch
                    else:
                        move_vals['dispatch_id'] = False
                move_obj.write(cr, uid, [move.id], move_vals)

            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
            for move in complete:
                defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
                if prodlot_ids.get(move.id):
                    defaults.update({'prodlot_id': prodlot_ids[move.id]})
                move_obj.write(cr, uid, [move.id], defaults)
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty': product_qty,
                    'product_uos_qty': product_qty,  # TODO: put correct uos_qty
                    'product_uom': product_uoms[move.id]
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)

            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking], context=context)
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = pick.id
                back_order_name = self.browse(cr, uid, delivered_pack_id, context=context).name
                self.message_post(cr, uid, new_picking, body=_("Back order <em>%s</em> has been <b>created</b>.") % (back_order_name), context=context)
            else:
                if 'carrier_id' in partial_datas and partial_datas['carrier_id']:
                    self.write(cr, uid, [pick.id], {'carrier_id': partial_datas['carrier_id']}, context=context)
                self.action_move(cr, uid, [pick.id], context=context)
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id

            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}

        return res


class StockMove(orm.Model):
    _inherit = 'stock.move'

    _columns = {
        'dispatch_state': fields.related('dispatch_id', 'state',
                                         type='char',
                                         relation='picking.dispatch',
                                         string='Dispatch State',
                                         readonly=True),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        """Override because in shortage context done moves are created from copies of undone moves
           We need dispatch_id information on done move"""
        if default is None:
            default = {}
        dispatch_id = False
        if 'dispatch_id' in default and default['dispatch_id']:
            dispatch_id = default['dispatch_id']
        default = default.copy()
        res = super(StockMove, self).\
            copy_data(cr, uid, id, default=default, context=context)
        if dispatch_id:
            res.update({'dispatch_id': dispatch_id})
        return res

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Inherited to allow the use of do_partial_via_dispatch()
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
