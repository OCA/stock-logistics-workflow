# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models
from openerp.osv import fields as osv_fields


class StockPackOperation(models.Model):

    _inherit = 'stock.pack.operation'

    # pylint: disable=old-api7-method-defined
    def _compute_lots_visible(
            self, cr, uid, ids, field_name, arg, context=None):
        res = super(StockPackOperation, self)._compute_lots_visible(
            cr, uid, ids, field_name=field_name, arg=arg, context=context)

        packs = self.browse(cr, uid, ids, context=context)

        pack_with_invisible_lots = packs.filtered(
            lambda p, r=res: r.get(p.id) and
            p.picking_id.picking_type_id.automatic_serial_generation and
            p.product_id.automatic_serial_generation and
            p.location_id.usage == 'supplier')
        for rec in pack_with_invisible_lots:
            res[rec.id] = False

        return res

    # pylint: disable=attribute-deprecated
    _columns = {
        'lots_visible': osv_fields.function(
            _compute_lots_visible,
            type='boolean',
        ),
    }

    @api.multi
    def _prepare_pack_ops_serials(self):
        """
        Generate a separate serial for each unit.
        :param vals: dictionnary containing attribute values to create a
        stock.pack.operation record.
        :return: [(0, 0, {qty:1, name: 'new generated serial}), (0, 0 , ...)]
        """
        sequence_model = self.env['ir.sequence']
        for rec in self:
            int_qty = int(rec.qty_done)
            pack_ops_lots = []
            while int_qty != 0:
                int_qty -= 1
                new_lot_name = sequence_model.next_by_code('stock.lot.serial')
                vals = {
                    'lot_name': new_lot_name,
                    'qty': 1,
                }
                pack_ops_lots.append((0, 0, vals))
            rec.write({'pack_lot_ids': pack_ops_lots})
        return True
