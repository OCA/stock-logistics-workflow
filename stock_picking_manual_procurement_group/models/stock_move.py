# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def action_confirm(self):
        for res in self:
            res._copy_group_from_picking()
        return super(StockMove, self).action_confirm()

    @api.multi
    def force_assign(self):
        for res in self:
            res._copy_group_from_picking()
        return super(StockMove, self).force_assign()

    @api.multi
    def _copy_group_from_picking(self):
        self.ensure_one()

        if not self.picking_id:
            return True

        picking = self.picking_id

        if not picking.create_procurement_group:
            return True

        self.write({"group_id": picking.group_id.id})
