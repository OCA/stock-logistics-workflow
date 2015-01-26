# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    locked = fields.Boolean(
        string='Locked', related="lot_id.locked", default=False,
        store=True)

    def quants_get(self, cr, uid, location, product, qty, domain=None,
                   restrict_lot_id=False, restrict_partner_id=False,
                   context=None):
        domain += [('locked', '=', False)]
        my_context = context.copy()
        my_context.update({'locked': False})
        return super(StockQuant, self).quants_get(
            cr, uid, location, product, qty, domain=domain,
            restrict_lot_id=restrict_lot_id,
            restrict_partner_id=restrict_partner_id, context=my_context)
