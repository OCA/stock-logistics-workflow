# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-15 Agile Business Group sagl (<http://www.agilebg.com>)
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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    product_uos_qty = fields.Float(
        'Quantity (UOS)',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    product_uos = fields.Many2one(
        "product.uom", string='Product UOS', readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(StockTransferDetails, self).default_get(fields)
        for item in res.get('item_ids'):
            pack_operation_model = self.env['stock.pack.operation']
            if (
                'packop_id' in item and
                len(pack_operation_model.browse(
                    item['packop_id']).linked_move_operation_ids) == 1
            ):
                p_uos = pack_operation_model.browse(
                    item['packop_id']).linked_move_operation_ids[0]. \
                    move_id.product_uos
                p_uos_qty = pack_operation_model.browse(
                    item['packop_id']).linked_move_operation_ids[0]. \
                    move_id.product_uos_qty
                item.update(
                    {
                        'product_uos': p_uos.id,
                        'product_uos_qty': p_uos_qty
                    }
                )
        return res


class StockTransferDetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    product_uos_qty = fields.Float(
        'Quantity (UOS)',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    product_uos = fields.Many2one(
        "product.uom", string='Product UOS', readonly=True)

    def onchange_product_uos_qty(
            self, cr, uid, ids, product_uos_qty, packop_id, context=None
    ):
        vals = {}
        warning = {}
        pack_operation = self.pool['stock.pack.operation'].browse(
            cr, uid, packop_id, context=context)
        if len(pack_operation.linked_move_operation_ids) > 1:
            warning.update({
                'title': _('Warning'),
                'message': _("The product_uos_qty changing do have any effect "
                             "in case the linked moves are more than one")})
        if len(pack_operation.linked_move_operation_ids) == 1:
            p_qty = pack_operation.linked_move_operation_ids[
                0].move_id.product_qty
            p_uos_qty = pack_operation.linked_move_operation_ids[
                0].move_id.product_uos_qty
            vals['quantity'] = p_qty * (product_uos_qty / p_uos_qty)

        return {'value': vals, 'warning': warning}
