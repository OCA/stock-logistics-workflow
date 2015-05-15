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
            'mrp_lock_lot.mt_lock_lot': lambda self, cr, uid, obj,
            ctx=None: obj.locked,
            'mrp_lock_lot.mt_unlock_lot': lambda self, cr, uid, obj,
            ctx=None: not obj.locked,
        },
    }

    @api.one
    def _get_locked_value(self):
        return self.product_id.categ_id.lot_default_locked

    locked = fields.Boolean(string='Blocked', default='_get_locked_value',
                            readonly=True)

    @api.one
    @api.onchange('product_id')
    def onchange_product_id(self):
        self.locked = self.product_id.categ_id.lot_default_locked

    @api.multi
    def button_lock(self):
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

    @api.model
    def create(self, vals):
        product = self.env['product.product']. browse(vals.get('product_id'))
        vals['locked'] = product.categ_id.lot_default_locked
        return super(StockProductionLot, self).create(vals)

    @api.one
    def write(self, values):
        if 'product_id' in values:
            product = self.env['product.product']. browse(
                values.get('product_id'))
            values['locked'] = product.categ_id.lot_default_locked
        return super(StockProductionLot, self).write(values)
