# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, _


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    @api.multi
    def _generate_pack_ops_serials(self):
        """ For pickings with operations matching certain condition, this
        method generate automatically the lots to be used in the transfer.
        The conditions are:
            - the Flag automatic serial generation has to set to True on
            the picking operation and on the operation product.
            - The tracking on the operation product has to be set to serial.
            - The qty to process is set.
        """
        for rec in self:
            if not rec.picking_type_id.automatic_serial_generation:
                continue
            auto_generate_ops = rec.pack_operation_ids.filtered(
                lambda op, pick=rec:
                op.product_id.tracking == 'serial' and
                op.product_id.automatic_serial_generation and
                op.qty_done)
            auto_generate_ops._prepare_pack_ops_serials()
        return True

    @api.multi
    def do_transfer(self):
        self._generate_pack_ops_serials()
        return super(StockPicking, self).do_transfer()

    @api.multi
    def do_new_transfer(self):

        # in the upstream and here in the override this function may
        # return a wizard hence it is logical to protect.
        self.ensure_one()
        if self.picking_type_id.automatic_serial_generation and \
           self.location_id.usage == 'supplier' and \
           (self.state == 'draft' or all(
                [x.qty_done == 0.0 for x in self.pack_operation_ids])):
            view = self.env.ref('stock.view_immediate_transfer')
            wizard = self.env['stock.immediate.transfer'].create(
                {'pick_id': self.id})
            return {
                'name': _(u"Immediate Transfer?"),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.immediate.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wizard.id,
                'context': self.env.context,
            }

        return super(StockPicking, self).do_new_transfer()
