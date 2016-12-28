# -*- coding: utf-8 -*-
# © 2016 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api
from __builtin__ import True


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.multi
    def action_assign(self):
        for record in self:
            super(StockMove, record.with_context(
                allow_not_blocked=record.location_dest_id.allow_locked)
            ).action_assign()
        return True

    @api.multi
    def action_scrap(self, quantity, location_id, restrict_lot_id=False,
                     restrict_partner_id=False):
        allow_locked = False if any(
            self.filtered(lambda r: not r.location_dest_id.allow_locked)) \
            else True
        return super(StockMove, self.with_context(
            allow_not_blocked=allow_locked)).action_scrap(
            quantity, location_id, restrict_lot_id=restrict_lot_id,
            restrict_partner_id=restrict_partner_id)

    @api.multi
    def action_done(self):
        allow_locked = False if any(
            self.filtered(lambda r: not r.location_dest_id.allow_locked)) \
            else True
        return super(StockMove, self.with_context(
            allow_not_blocked=allow_locked)).action_done()
