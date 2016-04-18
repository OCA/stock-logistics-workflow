# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, models
from openerp.exceptions import Warning
from openerp.tools.translate import _


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.multi
    def _prepare_move_vals(self, picking, quant, strap_location_id):
        self.ensure_one()
        move_obj = self.env['stock.move']
        product = quant.product_id
        res = move_obj.onchange_product_id(
            prod_id=product.id, loc_id=quant.location_id.id,
            loc_dest_id=strap_location_id)['value']
        res.update(move_obj.onchange_quantity(
            product.id, quant.qty, res['product_uom'], res['product_uos']
        )['value'])
        res.update({
            'product_id': product.id,
            'product_uom_qty': quant.qty,
            'picking_id': picking.id,
            'scrapped': True,
        })
        return res

    @api.multi
    def action_scrap_lot(self):
        self.ensure_one()
        if not self.quant_ids:
            raise Warning(_('Product list must be defined.'))
        move_obj = self.env['stock.move']
        strap_location_id = self.env.ref('stock.stock_location_scrapped').id
        picking = self.env['stock.picking'].create({
            'origin': 'Lot: %s' % self.name,
            'picking_type_id': self.env.ref('stock.picking_type_internal').id,
        })
        for quant in self.quant_ids:
            move = move_obj.create(self._prepare_move_vals(
                picking, quant, strap_location_id))
            quant.reservation_id = move.id
        if picking:
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.picking',
                'type': 'ir.actions.act_window',
                'res_id': picking.id,
                'context': self.env.context
            }
