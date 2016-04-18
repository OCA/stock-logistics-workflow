# -*- coding: utf-8 -*-
# © 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# © 2015 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
        return self._get_lock_reason(product) != 'none'

    def _get_lock_reason(self, product):
        """Reason to create locked

        @param product: browse-record for product.product"""
        _locked = product.categ_id.lot_default_locked
        categ = product.categ_id.parent_id
        while categ and not _locked:
            _locked = categ.lot_default_locked
            categ = categ.parent_id
        return _locked and 'category' or 'none'

    @api.one
    def _get_locked_value(self):
        return self._get_product_locked(self.product_id)

    locked = fields.Boolean(
        string='Blocked', default=lambda x: x._get_locked_value(),
        readonly=True)
    lock_reason = fields.Selection(
        selection=[('category', 'Demanded by product category'),
                   ('none', 'None')],
        string='Reason to block the lot',
        track_visibility='onchange')
    product_id = fields.Many2one(track_visibility='onchange')

    @api.one
    @api.onchange('product_id')
    def onchange_product_id(self):
        """Instruct the client to lock/unlock a lot on product change"""
        self.locked = self._get_product_locked(self.product_id)

    @api.multi
    def button_lock(self):
        """"Lock the lot if the reservations and permissions allow it"""
        if not self.user_has_groups('stock_lock_lot.group_lock_lot'):
            raise exceptions.AccessError(
                _('You are not allowed to block Serial Numbers/Lots'))
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
        """"Lock the lot if the permissions allow it"""
        if not self.user_has_groups('stock_lock_lot.group_lock_lot'):
            raise exceptions.AccessError(
                _('You are not allowed to unblock Serial Numbers/Lots'))
        return self.write({'locked': False})

    @api.model
    def create(self, vals):
        """Force the locking/unlocking, ignoring the value of 'locked'."""
        product = self.env['product.product'].browse(
            vals.get('product_id',
                     # Web quick-create provide in context
                     self.env.context.get('product_id', False)))
        vals['locked'] = self._get_product_locked(product)
        vals['lock_reason'] = self._get_lock_reason(product)
        return super(StockProductionLot, self).create(vals)

    @api.multi
    def write(self, values):
        """"Lock the lot if changing the product and locking is required"""
        if 'product_id' in values:
            product = self.env['product.product'].browse(values['product_id'])
            values['locked'] = self._get_product_locked(product)
            values['lock_reason'] = self._get_lock_reason(product)
        return super(StockProductionLot, self).write(values)
