# -*- coding: utf-8 -*-
# Copyright 2013-2015 Camptocamp SA - Nicolas Bessi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, models
from openerp.exceptions import UserError


class StockPicking(models.Model):
    """Adds picking split without done state."""

    _inherit = "stock.picking"

    @api.multi
    def split_process(self):
        """Use to trigger the wizard from button with correct context"""
        for pick in self:
            if pick.state == 'draft':
                raise UserError(_('Mark as todo this picking please.'))
            if all([x.qty_done == 0.0 for x in pick.pack_operation_ids]):
                raise UserError(
                    _('You must enter done quantity in order to split your '
                      'picking in several ones.'))
            wizard = self.env['stock.backorder.confirmation'].with_context(
                active_id=pick.id,
                do_only_split=True,
            ).create({})
            wizard.process()
