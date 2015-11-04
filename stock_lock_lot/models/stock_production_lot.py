# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class StockProductionLot(models.Model):
    _name = 'stock.production.lot'
    _inherit = ['stock.production.lot', 'mail.thread']

    _mail_post_access = 'read'
    _track = {
        'locked': {
            'stock_lock_lot.mt_lock_lot': lambda self, cr, uid, obj,
            ctx=None: obj.locked,
            'stock_lock_lot.mt_unlock_lot': lambda self, cr, uid, obj,
            ctx=None: not obj.locked,
        },
    }

    def _get_product_locked(self, product):
        """Should create locked? (including categories and parents)

        @param product: browse-record for product.product
        @return True when the category of the product or one of the parents
                demand new lots to be locked"""
        _locked = product.categ_id.lot_default_locked
        categ = product.categ_id.parent_id
        while categ and not _locked:
            _locked = categ.lot_default_locked
            categ = categ.parent_id
        return _locked

    @api.one
    def _get_locked_value(self):
        return self._get_product_locked(self.product_id)

    locked = fields.Boolean(string='Blocked', default='_get_locked_value',
                            readonly=True)

    @api.one
    @api.onchange('product_id')
    def onchange_product_id(self):
        '''Instruct the client to lock/unlock a lot on product change'''
        self.locked = self._get_product_locked(self.product_id)

    @api.multi
    def button_lock(self):
        '''Lock the lot if the reservations allow it'''
        stock_quant_obj = self.env['stock.quant']
        for lot in self:
            cond = [('lot_id', '=', lot.id),
                    ('reservation_id', '!=', False)]
            for quant in stock_quant_obj.search(cond):
                if quant.reservation_id.state not in ('cancel', 'done'):
                    raise exceptions.Warning(
                        _('Error! Serial Number/Lot "%s" currently has '
                          'reservations.')
                        % (lot.name))
        return self.write({'locked': True})

    @api.multi
    def button_unlock(self):
        return self.write({'locked': False})

    # Kept in old API to maintain compatibility
    def create(self, cr, uid, vals, context=None):
        '''Force the locking/unlocking, ignoring the value of 'locked'.'''
        product = self.pool['product.product'].browse(
            cr, uid, vals.get('product_id'))
        vals['locked'] = self._get_product_locked(product)
        return super(StockProductionLot, self).create(
            cr, uid, vals, context=context)

    @api.multi
    def write(self, values):
        '''Lock the lot if changing the product and locking is required'''
        if 'product_id' in values:
            product = self.env['product.product'].browse(
                values.get('product_id'))
            values['locked'] = self._get_product_locked(product)
        return super(StockProductionLot, self).write(values)
