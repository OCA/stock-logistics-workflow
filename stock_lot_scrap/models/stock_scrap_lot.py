# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.multi
    def _prepare_picking_vals(self, warehouse):
        return {
            'origin': _('Lot: %s') % self.name,
            'picking_type_id': warehouse.int_type_id.id or self.env.ref(
                'stock.picking_type_internal').id,
        }

    @api.multi
    def _prepare_move_vals(self, picking, quant, scrap_location_id):
        self.ensure_one()
        move_obj = self.env['stock.move']
        product = quant.product_id
        res = move_obj.onchange_product_id(
            prod_id=product.id, loc_id=quant.location_id.id,
            loc_dest_id=scrap_location_id)['value']
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
        quants = self.quant_ids.filtered(
            lambda x: x.location_id.usage == 'internal')
        if not quants:
            raise UserError(_("This lot doesn't contain any quant in internal "
                            "location."))
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        pickings = picking_obj.browse()
        scrap_location_id = self.env.ref('stock.stock_location_scrapped').id
        warehouse_ids = []
        for quant in quants.sorted(key=lambda x: x.history_ids[-1:].
                                   picking_id.picking_type_id.warehouse_id.id):
            warehouse = quant.history_ids[-1:].picking_id.picking_type_id.\
                warehouse_id
            if warehouse.id not in warehouse_ids:
                warehouse_ids.append(warehouse.id)
                picking = picking_obj.create(self._prepare_picking_vals(
                    warehouse))
                pickings |= picking
            move = move_obj.create(self._prepare_move_vals(
                picking, quant, scrap_location_id))
            quant.reservation_id = move.id

        result = self.env.ref('stock.action_picking_tree').read()[0]
        result['context'] = self.env.context
        if len(pickings) != 1:
            result['domain'] = "[('id', 'in', %s)]" % pickings.ids
        else:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pickings.id
        return result
