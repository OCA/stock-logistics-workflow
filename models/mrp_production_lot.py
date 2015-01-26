# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    locked = fields.Boolean(string='Locked', default=True)

    @api.multi
    def button_lock(self):
        self.ensure_one()
        stock_quant_obj = self.env['stock.quant']
        cond = [('lot_id', '=', self.id)]
        for quant in stock_quant_obj.search(cond):
            for move in quant.history_ids:
                if (move.location_dest_id and move.location_dest_id.usage in
                        ('view', 'internal')):
                    raise exceptions.Warning(
                        _('Error!: Found stock movements for this lot with'
                          ' location destination type in virtual/company'))
        return self.write({'locked': True})

    @api.multi
    def button_unlock(self):
        return self.write({'locked': False})
