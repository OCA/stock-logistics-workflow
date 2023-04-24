# Copyright 2016 Cyril Gaudin, Camptocamp SA
# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import float_is_zero


class StockPicking(models.Model):
    _inherit = "stock.picking"

    batch_id = fields.Many2one(string="Batch", domain="[('state', '=', 'draft')]",)

    def action_cancel(self):
        """In addition to what the method in the parent class does,
        cancel the batches for which all pickings are cancelled
        """
        result = super(StockPicking, self).action_cancel()
        self.mapped("batch_id").verify_state()

        return result

    def action_assign(self):
        """In addition to what the method in the parent class does,
        Changed batches states to assigned if all picking are assigned.
        """
        result = super(StockPicking, self).action_assign()
        self.mapped("batch_id").verify_state("assigned")

        return result

    def action_done(self):
        """In addition to what the method in the parent class does,
        Changed batches states to done if all picking are done.
        """
        result = super(StockPicking, self).action_done()
        self.mapped("batch_id").verify_state()

        return result

    def force_transfer(self, force_qty=True):
        """ Do the picking transfer (by calling action_done)

        If *force_qty* is True, force the transfer for all product_uom_qty
        when qty_done is 0.

        Otherwise, process only pack operation with qty_done.
        If a picking has no qty_done filled, we released it from his batch
        """
        for pick in self:
            if pick.state != "assigned":
                pick.action_assign()
                if pick.state != "assigned":
                    continue

            if force_qty:
                for pack in pick.move_line_ids:
                    pack.qty_done = pack.product_uom_qty
            else:
                if all(
                    float_is_zero(
                        pack.qty_done, precision_rounding=pack.product_uom_id.rounding
                    )
                    for pack in pick.move_line_ids
                ):
                    # No qties to process, release out of the batch
                    pick.batch_id = False
                    continue
                else:
                    for pack in pick.move_line_ids:
                        if not pack.qty_done:
                            pack.unlink()

            pick.action_done()
