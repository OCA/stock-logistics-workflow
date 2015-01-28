# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    def _get_locked_value(self):
        settings_obj = self.env['stock.config.settings']
        config = settings_obj.search([], limit=1, order='id DESC')
        return config.group_lot_default_locked

    locked = fields.Boolean(string='Locked', default=_get_locked_value,
                            readonly=True)

    @api.multi
    def button_lock(self):
        stock_quant_obj = self.env['stock.quant']
        for lot in self:
            cond = [('lot_id', '=', lot.id),
                    ('reservation_id', '!=', False)]
            for quant in stock_quant_obj.search(cond):
                for move in quant.history_ids:
                    if (move.location_dest_id and move.location_dest_id.usage
                            in ('view', 'internal') and move.state != 'done'):
                        raise exceptions.Warning(
                            _('Error!: Found stock movements for lot: "%" with'
                              ' location destination type in virtual/company')
                            % (lot.name))

        return self.write({'locked': True})

    @api.multi
    def button_unlock(self):
        return self.write({'locked': False})
