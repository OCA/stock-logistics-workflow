# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
#    Jon Chow <jon.chow@elico-corp.com>
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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class WizardPickingTrackingLine(orm.TransientModel):
    _name = 'wizard.picking.tracking.line'

    _columns = {
        'name': fields.char('name', size=32),
        'wizard_id': fields.many2one('wizard.picking.tracking', 'WPT'),
        'qty': fields.float('Pack Quantity'),
        'stock_move_id': fields.many2one('stock.move', 'Stock move'),
        'product_id': fields.related(
            'stock_move_id', 'product_id',
            type='many2one', relation='product.product',
            string='Product', readonly=True),
        'tracking_id': fields.related(
            'stock_move_id', 'tracking_id',
            type='many2one', relation='stock.tracking',
            string='Pack', readonly=True),
        'product_qty': fields.related(
            'stock_move_id', 'product_qty', type='float',
            string='Delivery Quantity', readonly=True),
    }

    def onchange_stock_move_id(
            self, cr, uid, ids, stock_move_id, context=None):
        move_obj = self.pool['stock.move']
        data = {
            'product_id': False,
            'tracking_id': False,
            'product_qty': 0,
            'qty': 0
        }
        if stock_move_id:
            stock_move = move_obj.browse(
                cr, uid, stock_move_id, context=context)
            product_id = stock_move.product_id and stock_move.product_id.id
            tracking_id = stock_move.tracking_id and \
                stock_move.tracking_id.id or False
            product_qty = stock_move.product_qty
            qty = not tracking_id and product_qty or 0.0
            data.update(
                {
                    'product_id': product_id,
                    'tracking_id': tracking_id,
                    'product_qty': product_qty,
                    'qty': qty
                })
        print '\n%s\n' % repr(data)
        return {'value': data}


class WizardPickingTracking(orm.TransientModel):
    _name = 'wizard.picking.tracking'

    def _get_serial(self, cr, uid, context=None):
        src_model = context.get('active_model')
        src_record = self.pool.get(src_model).browse(
            cr, uid, context.get('active_id', False))

        if src_model == 'stock.picking.out':
            return src_record.partner_id.ref
        elif src_model == 'stock.move':
            return src_record.picking_id.partner_id.ref
        else:
            return None

    def _get_lines(self, cr, uid, context=None):
        '''Get default move lines for the wizard.

        @return list of dict: a list of stock move records
        '''
        def _generate_stock_move(move):
            # filter out the ones which has already been packed or
            # quantity is 0.
            if (not move.tracking_id) or move.product_qty <= 0:
                data.append(
                    (0, 0, {
                        'stock_move_id': move.id,
                        'product_id': move.product_id.id,
                        'product_qty': move.product_qty,
                        'tracking_id': move.tracking_id and
                        move.tracking_id.id or False,
                        'qty': move.product_qty,
                    }))

        src_model = context.get('active_model')
        src_record = self.pool.get(src_model).browse(
            cr, uid, context.get('active_id', False))

        data = []
        # if the wizard is actived on stock picking level.
        if src_model == 'stock.picking.out':
            for move in src_record.move_lines:
                _generate_stock_move(move)
        # if the wizard is actived on stock move level
        elif src_model == 'stock.move':
            _generate_stock_move(src_record)

        # check the data is updated well
        return data

    def _get_picking(self, cr, uid, context=None):
        '''Get the default picking

        @return int: the id of the picking or False
        '''
        src_model = context.get('active_model')
        if src_model == 'stock.picking.out':
            return context.get('active_id', False)

        elif src_model == 'stock.move':
            stock_move = self.pool.get(src_model).browse(
                cr, uid, context.get('active_id', False))
            return stock_move and stock_move.picking_id and \
                stock_move.picking_id.id or False

    def _get_related_sale_order(self, src_model, src_record):
        '''Get the related sale order.

        @param src_model: the name of current model: stock.picking.out or
            stock.move
        @param src_record: the browse_record object of the model.
        @return: the browse_record object of sale order or False
        '''
        sale_order = False
        if not src_record:
            return sale_order
        if src_model == 'stock.picking.out':
            sale_order = src_record.sale_id
        elif src_model == 'stock.move':
            sale_order = src_record.picking_id and \
                src_record.picking_id.sale_id

        return sale_order

    def _get_pack_address(self, cr, uid, context=None):
        '''Get the partner shipping address from the related sale order.

        This function is used in the default function.

        @return string: the shippment address
        '''
        src_model = context.get('active_model')
        src_record = self.pool.get(src_model).browse(
            cr, uid, context.get('active_id', False), context=context)

        sale_order = self._get_related_sale_order(src_model, src_record)
        return sale_order and sale_order.partner_shipping_id and \
            sale_order.partner_shipping_id.name or False

    def _get_pack_note(self, cr, uid, context=None):
        '''Get the default pack note.

        Pack Num:Customer Name
        '''
        src_model = context.get('active_model', False)
        src_record = self.pool.get(src_model).browse(
            cr, uid, context.get('active_id', False), context=context)
        sale_order = self._get_related_sale_order(
            src_model, src_record)
        customer_name = sale_order and sale_order.partner_id.name or ''
        return customer_name

    def _get_default_ul(self, cr, uid, context=None):
        '''Get the default pack template

        get latest pack of current picking
        TODO improve the way of getting default pack template

        @return: ul id or False'''
        move_obj = self.pool['stock.move']
        src_model = context.get('active_model', False)
        src_record = self.pool.get(src_model).browse(
            cr, uid, context.get('active_id', False), context=context)
        default_ul_id = False
        latest_tracking = False

        # first get the current picking
        if src_model == 'stock.move':
            picking_id = src_record.picking_id and \
                src_record.picking_id.id or False
        elif src_model == 'stock.picking.out':
            picking_id = context.get('active_id')

        # searching the stock move with tracking id
        if picking_id:
            move_ids = move_obj.search(
                cr, uid,
                [('picking_id', '=', picking_id),
                 ('tracking_id', '!=', False)],
                limit=1,
                order='tracking_id DESC',
                context=context)
            if move_ids:
                latest_tracking = move_obj.browse(
                    cr, uid, move_ids[0], context=context).tracking_id
        if latest_tracking:
            default_ul_id = latest_tracking.ul_id and \
                latest_tracking.ul_id.id or False
        return default_ul_id

    _columns = {
        'name': fields.char('name', size=32, readonly=True),
        'picking_id': fields.many2one('stock.picking', 'Picking'),
        'ul_id': fields.many2one('product.ul', 'Pack Template', required=True),
        'lines': fields.one2many(
            'wizard.picking.tracking.line', 'wizard_id', 'Lines'),
        'pack_address': fields.char('Address', size=128),
        'pack_note': fields.char('Note', size=128),
        'gross_weight': fields.float('GW (Kg)'),
    }

    _defaults = {
        'lines': _get_lines,
        'picking_id': _get_picking,
        'pack_address': _get_pack_address,
        'pack_note': _get_pack_note,
        'ul_id': _get_default_ul,
    }

    def _action_check(self, wizard):
        '''Do some checks:
        - picking should not be in done state
        - pack quantity should always smaller than delivery quantity'''
        if wizard.picking_id.state == 'done':
            raise orm.except_orm(
                _('Warning!'),
                _("Wizard split pack can not be used when state is done !"))
        for line in wizard.lines:
            if line.qty > line.product_qty:
                raise orm.except_orm(
                    _('Warning!'),
                    _("New pack quantity can not "
                        "bigger than stock move quantity"))
        return True

    def action_split(self, cr, uid, ids, context=None):
        '''Split the current move and udpate the residual product qty;
        put the new stock move in a new pack.'''

        tracking_obj = self.pool['stock.tracking']
        stock_move_obj = self.pool['stock.move']
        procurement_obj = self.pool['procurement.order']

        wizard = self.browse(cr, uid, ids[0], context=context)
        self._action_check(wizard)

        tracking_values = {
            'ul_id': wizard.ul_id.id,
            'pack_address': wizard.pack_address,
            'pack_note': wizard.pack_note,
            'gross_weight': wizard.gross_weight,
            'move_ids': [],
        }

        new_pack_id = tracking_obj.create(
            cr, uid, tracking_values, context=context)

        for line in wizard.lines:
            stock_move = line.stock_move_id

            if not line.qty:
                continue

            res_product_qty = stock_move.product_qty - line.qty

            if res_product_qty:
                # update old stock move count procurement count
                stock_move_obj.write(
                    cr, uid, stock_move.id,
                    {'product_qty': res_product_qty},
                    context=context)

                procurement_id = stock_move.procurements and \
                    stock_move.procurements[0].id or False
                if procurement_id:
                    procurement_obj.write(
                        cr, uid, procurement_id,
                        {'product_uos_qty': res_product_qty,
                         'product_qty': res_product_qty},
                        context=context)
                # create the new move and assign the pack to the move.
                new_move_data = stock_move_obj.copy_data(
                    cr, uid, stock_move.id,
                    default={
                        'product_qty': line.qty,
                        'product_uos_qty': line.qty,
                        'tracking_id': new_pack_id,
                        'procurements': False,
                        'state': stock_move.state
                    }, context=context)
                new_move_id = stock_move_obj.create(
                    cr, uid, new_move_data, context=context)
                # if there is procurement order,
                # we create the procurement order
                if procurement_id:
                    procurement_data = procurement_obj.copy_data(
                        cr, uid, procurement_id, default={
                            'product_uos_qty': line.qty,
                            'product_qty': line.qty,
                            'move': new_move_id,
                        })
                    procurement_obj.create(
                        cr, uid, procurement_data, context=context)
            else:
                # if not res_product_qty, only to change the package
                stock_move_obj.write(
                    cr, uid, stock_move.id,
                    {'tracking_id': new_pack_id}, context=context)

        # return new_pack_id
        return {
            'name': _('Pack Split'),
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'stock.picking.out',
            'res_id': wizard.picking_id.id,
            'type': 'ir.actions.act_window',
        }

    def action_split_and_new(self, cr, uid, ids, context=None):
        '''This is for the button: save & new in the wizard form'''

        res = self.action_split(cr, uid, ids, context=context)
        res.update({
            'target': 'new',
            'context': {
                'active_id': context.get('active_id'),
                'active_ids': context.get('active_ids'),
                'active_model': context.get('active_model')
            },
            'res_id': False,
            'res_model': 'wizard.picking.tracking'
        })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
