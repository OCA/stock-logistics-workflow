# -*- coding: utf-8 -*-
# @2016 Cyril Gaudin, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    batch_picking_id = fields.Many2one(
        comodel_name='stock.batch.picking',
        string='Batch',
        copy=False,
        domain="[('state', '=', 'draft')]",
        help='In which batch picking this picking will be processed.'
    )

    @api.multi
    def action_cancel(self):
        """In addition to what the method in the parent class does,
        cancel the batches for which all pickings are cancelled
        """
        # we need to unreserve the picking before canceling it as other way
        # it will still have the pack_operation_ids, which will be seen
        # in the report, which is undesirable
        self.do_unreserve()
        result = super(StockPicking, self).action_cancel()
        self.mapped('batch_picking_id').verify_state()

        return result

    @api.multi
    def action_assign(self):
        """In addition to what the method in the parent class does,
        Changed batches states to assigned if all picking are assigned.
        """
        result = super(StockPicking, self).action_assign()
        self.mapped('batch_picking_id').verify_state('assigned')

        return result

    @api.multi
    def do_transfer(self):
        """In addition to what the method in the parent class does,
        Changed batches states to done if all picking are done.
        """
        result = super(StockPicking, self).do_transfer()
        self.mapped('batch_picking_id').verify_state()

        return result

    def force_transfer(self, force_qty=True):
        """ Do the picking transfer (by calling do_transfer)

        If *force_qty* is True, force the transfer for all product_qty
        when qty_done is 0.

        Otherwise, process only pack operation with qty_done.
        If a picking has no qty_done filled, we released it from his batch
        """
        for pick in self:
            if pick.state != 'assigned':
                pick.action_assign()
                if pick.state != 'assigned':
                    continue

            if force_qty:
                for pack in pick.pack_operation_ids:
                    pack.qty_done = pack.product_qty
            else:
                if all(pack.qty_done == 0 for pack in pick.pack_operation_ids):
                    # No qties to process, release out of the batch
                    pick.batch_picking_id = False
                    continue
                else:
                    for pack in pick.pack_operation_ids:
                        if not pack.qty_done:
                            pack.unlink()
                        else:
                            pack.product_qty = pack.qty_done

            pick.do_transfer()
