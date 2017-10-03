# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models
# pylint: disable=deprecated-module
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

    @api.model
    def _generate_new_serial_name(self, operation=False):
        """
        This method generate a new serial number each time
        it's called. This method is meant to be overridden in case
        a different sequence applied for automatically generated
        serials or a different sequence is applied by product.
        @param operation: `stock.pack.operation` record
        @return str: new serial number
        """
        return self.env['ir.sequence'].next_by_code('stock.lot.serial')

    @api.multi
    def _prepare_pack_ops_serials(self):
        """
        Generate a separate serial for each unit.
        :param vals: dictionnary containing attribute values to create a
        stock.pack.operation record.
        :return: [(0, 0, {qty:1, name: 'new generated serial}), (0, 0 , ...)]
        """
        for rec in self:
            pack_ops_lots = []
            for i in range(int(rec.qty_done)):
                vals = {
                    'lot_name': self._generate_new_serial_name(operation=rec),
                    'qty': 1,
                }
                pack_ops_lots.append((0, 0, vals))
            rec.write({'pack_lot_ids': pack_ops_lots})
        return True
